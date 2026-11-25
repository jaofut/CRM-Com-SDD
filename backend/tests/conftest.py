import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.usuario import PerfilUsuario, Usuario


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSession()
    try:
        admin = Usuario(
            nome="Admin Teste",
            email="admin@teste.local",
            senha_hash=hash_password("123456"),
            perfil=PerfilUsuario.ADMIN,
            ativo=True,
        )
        atendente = Usuario(
            nome="Atendente Teste",
            email="atendente@teste.local",
            senha_hash=hash_password("123456"),
            perfil=PerfilUsuario.ATENDENTE,
            ativo=True,
        )
        db.add_all([admin, atendente])
        db.commit()
        db.refresh(admin)
        db.refresh(atendente)
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(db_session):
    admin = db_session.query(Usuario).filter(Usuario.email == "admin@teste.local").first()
    token = create_access_token(admin.id, admin.perfil)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def atendente_headers(db_session):
    atendente = db_session.query(Usuario).filter(Usuario.email == "atendente@teste.local").first()
    token = create_access_token(atendente.id, atendente.perfil)
    return {"Authorization": f"Bearer {token}"}
