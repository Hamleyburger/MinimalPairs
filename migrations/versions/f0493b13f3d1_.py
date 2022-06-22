"""empty message

Revision ID: f0493b13f3d1
Revises: ea05ad3a2dab
Create Date: 2022-06-22 19:29:14.098871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0493b13f3d1'
down_revision = 'ea05ad3a2dab'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('news') as batch_op:
        batch_op.add_column(sa.Column('imagepath', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('news') as batch_op:
        batch_op.drop_column('imagepath')