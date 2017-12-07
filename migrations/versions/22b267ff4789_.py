"""init

Revision ID: 22b267ff4789
Revises: 
Create Date: 2017-12-07 17:09:19.568554

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from coaster.sqlalchemy import JsonDict

# revision identifiers, used by Alembic.
revision = '22b267ff4789'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
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
    op.create_table('mail_account',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('email', sa.Unicode(length=254), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table('auto_responder',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('template', sa.UnicodeText(), nullable=True),
        sa.Column('pattern_rel', sa.Unicode(length=255), nullable=False),
        sa.Column('pattern_text', sa.Unicode(length=255), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['mail_account.id'], ),
        sa.PrimaryKeyConstraint('id')
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
    op.create_table('subscriber',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.Unicode(length=254), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['mail_account.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table('subscription',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('subscriber_id', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('unsubscribed_at', sa.DateTime(), nullable=True),
        sa.Column('resubscribed_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['mail_account.id'], ),
        sa.ForeignKeyConstraint(['subscriber_id'], ['mail_account.id'], ),
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
    op.drop_table('subscriber')
    op.drop_table('mail_thread')
    op.drop_table('auto_responder')
    op.drop_table('mail_account')
    op.drop_table('user')
