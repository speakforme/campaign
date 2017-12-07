"""init

Revision ID: 7b2ca94220c3
Revises: 
Create Date: 2017-12-07 23:57:40.796880

"""
from alembic import op
import sqlalchemy as sa
from coaster.sqlalchemy import JsonDict
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '7b2ca94220c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('organization',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('userid', sa.Unicode(length=22), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=250), nullable=False),
    sa.Column('title', sa.Unicode(length=250), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('userid')
    )
    op.create_table('user',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('userid', sa.String(length=22), nullable=False),
    sa.Column('lastuser_token_scope', sa.Unicode(length=250), nullable=True),
    sa.Column('lastuser_token_type', sa.Unicode(length=250), nullable=True),
    sa.Column('userinfo', JsonDict(), nullable=True),
    sa.Column('email', sa.Unicode(length=80), nullable=True),
    sa.Column('lastuser_token', sa.String(length=22), nullable=True),
    sa.Column('username', sa.Unicode(length=80), nullable=True),
    sa.Column('fullname', sa.Unicode(length=80), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('lastuser_token'),
    sa.UniqueConstraint('userid'),
    sa.UniqueConstraint('username')
    )
    op.create_table('campaign',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.Unicode(length=250), nullable=False),
    sa.Column('title', sa.Unicode(length=250), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('mail_account',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('email', sa.Unicode(length=254), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('subscriber',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=254), nullable=False),
    sa.Column('first_name', sa.Unicode(length=255), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('mail_thread',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.Unicode(length=255), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['mail_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscription',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('campaign_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('subscriber_id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('unsubscribed_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaign.id'], ),
    sa.ForeignKeyConstraint(['subscriber_id'], ['subscriber.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mail_message',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('from_address', sa.Unicode(length=254), nullable=False),
    sa.Column('headers', JsonDict(), nullable=False),
    sa.Column('thread_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.ForeignKeyConstraint(['thread_id'], ['mail_thread.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('mail_message')
    op.drop_table('subscription')
    op.drop_table('mail_thread')
    op.drop_table('subscriber')
    op.drop_table('mail_account')
    op.drop_table('campaign')
    op.drop_table('user')
    op.drop_table('organization')
