"""Add number column to TestCase

Revision ID: 80890bf49a2c
Revises: afd06e1450de
Create Date: 2025-04-03 11:33:29.653374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80890bf49a2c'
down_revision = 'afd06e1450de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_case', schema=None) as batch_op:
        batch_op.add_column(sa.Column('number', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_case', schema=None) as batch_op:
        batch_op.drop_column('number')

    # ### end Alembic commands ###
