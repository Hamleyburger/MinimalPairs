"""empty message

Revision ID: f5ef1d0499d9
Revises: f57438cba477
Create Date: 2022-05-26 08:56:43.020227

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'f5ef1d0499d9'
down_revision = 'f57438cba477'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('images') as batch_op:
        batch_op.add_column(sa.Column('time_created', sa.DateTime(), default=func.current_timestamp()))
#        batch_op.add_column('time_updated', sa.Column(sa.DateTime(), onupdate=func.now()))


def downgrade():
    with op.batch_alter_table('images') as batch_op:
        batch_op.drop_column('time_created')
#        batch_op.drop_column('time_updated')
