"""Add stuff

Revision ID: 2bacde5658d3
Revises: e1d378c78c9d
Create Date: 2018-07-17 16:04:49.914071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bacde5658d3'
down_revision = 'e1d378c78c9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('csv_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requirement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pos_in_csv', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_status_name'), 'status', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_status_name'), table_name='status')
    op.drop_table('status')
    op.drop_table('requirement')
    op.drop_table('csv_entry')
    # ### end Alembic commands ###