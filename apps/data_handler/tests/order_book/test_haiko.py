import pytest
from decimal import Decimal
from unittest.mock import patch

from apps.data_handler.handlers.order_books.haiko.main import HaikoOrderBook


class TestHaikoOrderBook:
    VALID_TOKEN_PAIRS = [
        (
            "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",  # ETH
            "0x53c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",  # USDC
        ),
    ]

    def test_init_valid_tokens(self):
        """Test initialization with valid token pair"""
        for token_a, token_b in self.VALID_TOKEN_PAIRS:
            order_book = HaikoOrderBook(token_a, token_b)
            assert order_book.token_a == token_a
            assert order_book.token_b == token_b

    def test_invalid_token_addresses(self):
        """Test initialization with invalid token addresses"""
        with pytest.raises(
            ValueError,
        ):
            HaikoOrderBook("0xinvalid1", "0xinvalid2")

    @patch("apps.data_handler.handlers.order_books.haiko.main.HaikoOrderBook")
    def test_usd_price_retrieval(self, mock_connector):
        """Test USD price retrieval functionality"""

        mock_connector.return_value.get_usd_prices.return_value = {
            "wstETH": Decimal("1850.50"),
            "ETH": Decimal("1850.50"),
        }

        token_a, token_b = self.VALID_TOKEN_PAIRS[0]
        order_book = HaikoOrderBook(token_a, token_b)

        assert order_book.token_a_price > 0
        assert order_book.token_b_price > 0

    def test_price_calculation(self):
        """Test price calculation methods"""
        token_a, token_b = self.VALID_TOKEN_PAIRS[0]
        order_book = HaikoOrderBook(token_a, token_b)

        test_tick = Decimal("100")
        price = order_book.tick_to_price(test_tick)
        assert isinstance(price, Decimal)
        assert price > 0

    @pytest.mark.skip("Need to fix this test")
    @patch("apps.data_handler.handlers.order_books.haiko.main.HaikoAPIConnector")
    @patch("apps.data_handler.handlers.order_books.haiko.main.HaikoBlastAPIConnector")
    def test_fetch_price_and_liquidity(
        self, mock_blast_connector, mock_haiko_connector
    ):
        """Test fetch price and liquidity with mocked API responses"""
        mock_instance = mock_haiko_connector.return_value
        mock_instance.get_supported_tokens.return_value = self.VALID_TOKEN_PAIRS[0]
        mock_instance.get_pair_markets.return_value = [
            {
                "marketId": "market1",
                "baseToken": {"address": self.VALID_TOKEN_PAIRS[0][0]},
                "quoteToken": {"address": self.VALID_TOKEN_PAIRS[0][1]},
                "currPrice": "1850.50",
                "tvl": "1000000",
            }
        ]

        mock_blast_connector.get_block_info.return_value = {
            "result": {"block_number": 12345, "timestamp": 1625097600}
        }

        mock_instance.get_market_depth.return_value = [
            {"price": "1800", "liquidityCumulative": "100000"},
            {"price": "1900", "liquidityCumulative": "50000"},
        ]

        token_a, token_b = self.VALID_TOKEN_PAIRS[0]
        order_book = HaikoOrderBook(token_a, token_b)
        order_book.fetch_price_and_liquidity()

        assert order_book.block is not None
        assert order_book.timestamp is not None
        assert len(order_book.asks) > 0
        assert len(order_book.bids) > 0

    def test_token_amount_calculation(self):
        """Test token amount calculation method"""
        token_a, token_b = self.VALID_TOKEN_PAIRS[0]
        order_book = HaikoOrderBook(token_a, token_b)

        current_liq = Decimal("100000")
        current_sqrt = Decimal("42.123")
        next_sqrt = Decimal("43.456")

        ask_amount = order_book._get_token_amount(current_liq, current_sqrt, next_sqrt)
        assert isinstance(ask_amount, Decimal)
        assert ask_amount > 0

        bid_amount = order_book._get_token_amount(
            current_liq, current_sqrt, next_sqrt, is_ask=False
        )
        assert isinstance(bid_amount, Decimal)
        assert bid_amount > 0

    def test_serialization(self):
        """Test order book serialization"""
        token_a, token_b = self.VALID_TOKEN_PAIRS[0]
        order_book = HaikoOrderBook(token_a, token_b)
        order_book.fetch_price_and_liquidity()

        serialized_data = order_book.serialize()
        dict_data = serialized_data.dict()
        assert isinstance(dict_data, dict)
        assert "asks" in dict_data
        assert "bids" in dict_data
