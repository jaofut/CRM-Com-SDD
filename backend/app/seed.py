from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import PerfilUsuario, Usuario


def seed_initial_users() -> None:
    db = SessionLocal()
    try:
        defaults = [
            ("Administrador Oficina", "admin@oficina.com", "admin123", PerfilUsuario.ADMIN),
            ("Atendente Balcao", "atendente@oficina.com", "atendente123", PerfilUsuario.ATENDENTE),
        ]
        for nome, email, senha, perfil in defaults:
            existing = db.scalar(select(Usuario).where(Usuario.email == email))
            if not existing:
                db.add(
                    Usuario(
                        nome=nome,
                        email=email,
                        senha_hash=hash_password(senha),
                        perfil=perfil,
                        ativo=True,
                    )
                )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_initial_users()
    print("Seed concluído com sucesso.")
