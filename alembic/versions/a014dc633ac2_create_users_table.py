"""create users table

Revision ID: a014dc633ac2
Revises: 
Create Date: 2023-02-15 22:19:13.665102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a014dc633ac2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('date_created', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('transactions',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('exchange_rate', sa.Float(), nullable=True),
                    sa.Column('buy_BTC', sa.Float(), nullable=True),
                    sa.Column('sale', sa.Float(), nullable=True),
                    sa.Column('currency_id', sa.Integer(), nullable=True),
                    sa.Column('wallets', sa.Text(), nullable=True),
                    sa.Column('date_created', sa.DateTime(), nullable=True),
                    sa.Column('approved', sa.Boolean, nullable=True),
                    sa.Column('check', sa.Text, nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['currency_id'], ['currency.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('referrals',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('referral', sa.BigInteger(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('currency',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('name', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('wallets',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('address', sa.Text(), nullable=True),
                    sa.Column('wif', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('transactions')
    op.drop_table('referrals')
    op.drop_table('currency')
    op.drop_table('wallets')
