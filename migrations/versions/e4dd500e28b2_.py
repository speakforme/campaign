"""add auto responder

Revision ID: e4dd500e28b2
Revises: 7b2ca94220c3
Create Date: 2017-12-08 18:13:00.954210

"""
from alembic import op
import sqlalchemy_utils
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4dd500e28b2'
down_revision = '7b2ca94220c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('auto_responder',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('campaign_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column('subject', sa.Unicode(length=255), nullable=False),
        sa.Column('template', sa.UnicodeText(), nullable=True),
        sa.Column('frequency', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaign.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('auto_responder')
