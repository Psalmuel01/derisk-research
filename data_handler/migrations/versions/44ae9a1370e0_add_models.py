"""add models

Revision ID: 44ae9a1370e0
Revises: 
Create Date: 2024-06-02 01:00:09.291876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

from handlers.liquidable_debt.values import LendingProtocolNames
from tools.constants import ProtocolIDs

# revision identifiers, used by Alembic.
revision: str = '44ae9a1370e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('liquidable_debt',
    sa.Column('protocol', sqlalchemy_utils.types.choice.ChoiceType(LendingProtocolNames, impl=sa.String()), nullable=False),
    sa.Column('user', sa.String(), nullable=False),
    sa.Column('liquidable_debt', sa.DECIMAL(), nullable=False),
    sa.Column('health_factor', sa.DECIMAL(), nullable=False),
    sa.Column('collateral', sa.JSON(), nullable=False),
    sa.Column('risk_adjusted_collateral', sa.DECIMAL(), nullable=False),
    sa.Column('debt', sa.JSON(), nullable=False),
    sa.Column('debt_usd', sa.DECIMAL(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_liquidable_debt_user'), 'liquidable_debt', ['user'], unique=False)
    op.create_table('loan_state',
    sa.Column('block', sa.BigInteger(), nullable=True),
    sa.Column('timestamp', sa.BigInteger(), nullable=True),
    sa.Column('protocol_id', sqlalchemy_utils.types.choice.ChoiceType(ProtocolIDs, impl=sa.String()), nullable=False),
    sa.Column('user', sa.String(), nullable=True),
    sa.Column('collateral', sa.JSON(), nullable=True),
    sa.Column('debt', sa.JSON(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loan_state_block'), 'loan_state', ['block'], unique=False)
    op.create_index(op.f('ix_loan_state_timestamp'), 'loan_state', ['timestamp'], unique=False)
    op.create_index(op.f('ix_loan_state_user'), 'loan_state', ['user'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_loan_state_user'), table_name='loan_state')
    op.drop_index(op.f('ix_loan_state_timestamp'), table_name='loan_state')
    op.drop_index(op.f('ix_loan_state_block'), table_name='loan_state')
    op.drop_table('loan_state')
    op.drop_index(op.f('ix_liquidable_debt_user'), table_name='liquidable_debt')
    op.drop_table('liquidable_debt')
    # ### end Alembic commands ###
