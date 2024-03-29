"""empty message

Revision ID: 7baf30b80e46
Revises: 
Create Date: 2021-09-19 21:43:56.560096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7baf30b80e46'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('searched_pairs', sa.Column('existing_pairs', sa.Integer(), nullable=True))
    op.drop_column('userimages', 'cropped')
    op.drop_column('words', 'times_used')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('words', sa.Column('times_used', sa.INTEGER(), nullable=True))
    op.add_column('userimages', sa.Column('cropped', sa.BOOLEAN(), nullable=True))
    op.drop_column('searched_pairs', 'existing_pairs')
    # ### end Alembic commands ###
