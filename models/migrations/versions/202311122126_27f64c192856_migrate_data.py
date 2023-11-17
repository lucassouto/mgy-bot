"""migrate_data

Revision ID: 27f64c192856
Revises: b3faf853662b
Create Date: 2023-11-12 21:26:56.317453

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "27f64c192856"
down_revision: str | None = "b3faf853662b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Migrate level data
    op.execute(
        "INSERT INTO levels (id, value, name, created_at, updated_at) SELECT id_niveis, id_niveis, nome_nivel, NOW(), NOW() FROM niveis"
    )

    # Migrate musics data
    op.execute(
        "INSERT INTO musics (id, name, url, user_id, title, created_at, updated_at) SELECT id_musicas, name, url, user_id, title, NOW(), NOW() FROM music_links"
    )

    # Migrate servers data
    op.execute(
        "INSERT INTO servers (id, name, discord_id, created_at, updated_at) SELECT id_servidores, nome_servidor, numero_id_servidor, NOW(), NOW() FROM servidores"
    )

    # Migrate users data
    op.execute(
        "INSERT INTO users (id, name, discord_user_id, level_id, experience, server_id, youtube, twitch, twitter, others, total_messages, created_at, updated_at) "
        "SELECT id_usuarios, nome_usuario, user_id_discord, nivel_id, CAST(experiencia AS INTEGER), servidor_id, youtube, twitch, twitter, outros, total_mensagens, NOW(), NOW() "
        "FROM usuarios"
    )


def downgrade() -> None:
    op.execute("DELETE FROM levels")
    op.execute("DELETE FROM musics")
    op.execute("DELETE FROM servers")
    op.execute("DELETE FROM users")
