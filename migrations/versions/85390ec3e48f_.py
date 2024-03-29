"""empty message

Revision ID: 85390ec3e48f
Revises: 40e82171901b
Create Date: 2022-08-10 22:17:19.374626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85390ec3e48f'
down_revision = '40e82171901b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('soundpairs',
    sa.Column('sound_id', sa.Integer(), nullable=False),
    sa.Column('pair_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pair_id'], ['pairs.id'], ),
    sa.ForeignKeyConstraint(['sound_id'], ['sounds.id'], ),
    sa.PrimaryKeyConstraint('sound_id', 'pair_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('soundpairs')
    # ### end Alembic commands ###
