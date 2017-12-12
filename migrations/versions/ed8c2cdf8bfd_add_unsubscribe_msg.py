"""add_unsubscribe_msg

Revision ID: ed8c2cdf8bfd
Revises: 067db314c9ee
Create Date: 2017-12-13 02:25:13.308338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed8c2cdf8bfd'
down_revision = '067db314c9ee'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('campaign', sa.Column('unsubscribe_msg', sa.UnicodeText(), nullable=True))


def downgrade():
    op.drop_column('campaign', 'unsubscribe_msg')
