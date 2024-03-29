"""empty message

Revision ID: c379b4b2dd44
Revises: cb82304b8d72
Create Date: 2022-07-15 10:17:01.437064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c379b4b2dd44'
down_revision = 'cb82304b8d72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isinitial', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_column('isinitial')

    # ### end Alembic commands ###
