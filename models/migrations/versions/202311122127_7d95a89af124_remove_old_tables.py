"""remove_old_tables

Revision ID: 7d95a89af124
Revises: 27f64c192856
Create Date: 2023-11-12 21:27:27.620053

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d95a89af124"
down_revision: str | None = "27f64c192856"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("niveis")
    op.drop_table("servidores")
    op.drop_table("usuarios")
    op.drop_table("music_links")


def downgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id_usuarios", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("nome_usuario", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("user_id_discord", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("nivel_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "experiencia", sa.VARCHAR(length=45), server_default=sa.text("0"), autoincrement=False, nullable=False
        ),
        sa.Column("servidor_id", sa.INTEGER(), server_default=sa.text("0"), autoincrement=False, nullable=False),
        sa.Column("youtube", sa.VARCHAR(length=200), autoincrement=False, nullable=True),
        sa.Column("twitch", sa.VARCHAR(length=200), autoincrement=False, nullable=True),
        sa.Column("twitter", sa.VARCHAR(length=200), autoincrement=False, nullable=True),
        sa.Column("outros", sa.VARCHAR(length=2000), autoincrement=False, nullable=True),
        sa.Column("total_mensagens", sa.INTEGER(), server_default=sa.text("0"), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["servidor_id"], ["servidores.id_servidores"], name="fk_numero_id_servidor"),
        sa.PrimaryKeyConstraint("id_usuarios", name="usuarios_pkey"),
    )
    op.create_table(
        "servidores",
        sa.Column("id_servidores", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("nome_servidor", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("numero_id_servidor", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id_servidores", name="servidores_pkey"),
    )
    op.create_table(
        "niveis",
        sa.Column("id_niveis", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("nome_nivel", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    )
    op.create_table(
        "music_links",
        sa.Column("id_musicas", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("url", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("title", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    )
