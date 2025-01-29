"""Add ticket_id to Booking model

Revision ID: 312b2833f259
Revises: 6a7aea8de74c
Create Date: 2025-01-27 13:13:05.831839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '312b2833f259'
down_revision = '6a7aea8de74c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ticket_id', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_column('ticket_id')

    # ### end Alembic commands ###
