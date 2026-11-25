from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    auth,
    clientes,
    crm,
    dashboard,
    orcamentos,
    ordens_servico,
    usuarios,
    veiculos,
)
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_router = APIRouter(prefix=settings.API_V1_PREFIX)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(usuarios.router)
api_v1_router.include_router(clientes.router)
api_v1_router.include_router(veiculos.router)
api_v1_router.include_router(orcamentos.router)
api_v1_router.include_router(ordens_servico.router)
api_v1_router.include_router(crm.router)
api_v1_router.include_router(dashboard.router)

app.include_router(api_v1_router)


@app.get("/health")
def health():
    return {"status": "ok"}
