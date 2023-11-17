"""initial_migration

Revision ID: b3faf853662b
Revises: 
Create Date: 2023-11-12 21:25:43.323144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3faf853662b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('levels',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('servers',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('discord_id', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('discord_user_id', sa.String(), nullable=False),
    sa.Column('level_id', sa.Integer(), sa.ForeignKey('levels.id'), nullable=False),
    sa.Column('server_id', sa.Integer(), sa.ForeignKey('servers.id'), nullable=False),
    sa.Column('experience', sa.Integer(), nullable=False),
    sa.Column('youtube', sa.String(), nullable=True),
    sa.Column('twitch', sa.String(), nullable=True),
    sa.Column('twitter', sa.String(), nullable=True),
    sa.Column('others', sa.String(), nullable=True),
    sa.Column('total_messages', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key('fk_users_levels', 'users', 'levels', ['level_id'], ['id'])
    op.create_foreign_key('fk_users_servers', 'users', 'servers', ['server_id'], ['id'])
    op.create_table('musics',
    sa.Column('name', sa.String(), autoincrement=False, nullable=False),
    sa.Column('url', sa.String(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.String(), autoincrement=False, nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('servers')
    op.drop_table('levels')
    op.drop_table('musics')
    # ### end Alembic commands ###
