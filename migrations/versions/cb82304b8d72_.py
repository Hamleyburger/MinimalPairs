"""empty message

Revision ID: cb82304b8d72
Revises: f0493b13f3d1
Create Date: 2022-07-14 21:31:13.317765

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb82304b8d72'
down_revision = 'f0493b13f3d1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pairs', sa.Column('isinitial', sa.Boolean(), nullable=True))

        #batch_op.add_column('time_updated', sa.Column(sa.DateTime(), onupdate=func.now()))


def downgrade():
    op.drop_column('pairs', 'isinitial')