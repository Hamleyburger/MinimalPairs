"""empty message

Revision ID: 40e82171901b
Revises: 9ae394f41bc4
Create Date: 2022-08-10 20:53:41.382915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40e82171901b'
down_revision = '9ae394f41bc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('soundpairs',
    sa.Column('sound_id', sa.Integer(), nullable=True),
    sa.Column('pair_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pair_id'], ['pairs.id'], ),
    sa.ForeignKeyConstraint(['sound_id'], ['sounds.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('soundpairs')
    # ### end Alembic commands ###