# Implementation Plan: CRM para Oficina de Veículos de Grande Porte

**Branch**: `001-crm-oficina-pesados` | **Date**: 2026-11-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-crm-oficina-pesados/spec.md`

## Summary

Construir um CRM web voltado para oficina de veículos de grande porte (frotas/transportadoras B2B), cobrindo cadastro estruturado de clientes/contatos/motoristas/veículos, funil visual (Kanban) de orçamentos com geração de PDF e atalho para WhatsApp Web, conversão direta para Ordem de Serviço (OS) com checklist simplificado de entrada/saída, timeline de interações, lembretes de manutenção preventiva e painel gerencial com controle de acesso em 2 perfis (`ADMIN` e `ATENDENTE`).

A arquitetura adota **FastAPI + SQLAlchemy 2.0 + Alembic + SQLite local** no backend e **Next.js (App Router) + TypeScript + Tailwind CSS** no frontend.

## Technical Context

**Language/Version**: Python 3.11+ (Backend) / TypeScript 5+ com Node.js 20+ (Frontend)

**Primary Dependencies**:
- Backend: FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PyJWT, bcrypt/pwdlib, ReportLab (PDF)
- Frontend: Next.js (App Router), React 19, Tailwind CSS, shadcn/ui, Lucide Icons

**Storage**: SQLite local (`backend/data/crm.db`) com `PRAGMA foreign_keys=ON` e `WAL` mode

**Testing**: `pytest` + `httpx` (Backend API & regras de negócio); `Vitest` + `tsc --noEmit` (Frontend)

**Target Platform**: Aplicação Web local/intranet (Windows/Linux) rodando em navegador desktop/tablet

**Project Type**: Web application (`backend/` + `frontend/`)

**Performance Goals**: Busca global por CNPJ ou placa `< 2s`; carregamento do Kanban de orçamentos e fila de OS `< 500ms` em base local

**Constraints**: Sem dependências de serviços externos obrigatórios na v1 (sem API oficial WhatsApp, sem NF-e, sem banco externo); geração de PDF 100% compatível com Windows sem binários nativos extras

**Scale/Scope**: 1 oficina, ~5–15 usuários simultâneos, milhares de veículos/OS no SQLite local

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- `.specify/memory/constitution.md` (`v1.0.0`, ratificada em `2026-11-24`) verificada e atendida: separação de camadas (`api/v1`, `schemas`, `services`, `models`), SQLite com `WAL`/`FK` e preservação histórica, testes `pytest`/`httpx` nas regras críticas, escopo autocontido (YAGNI) e RBAC no backend.
- **Verificação de boas práticas (pré e pós-design)**:
  - Separação clara entre camadas de API (`routers`), regras de negócio (`services`), modelos (`models`) e contratos (`schemas`).
  - Todas as regras críticas do `spec.md` (unicidade de CNPJ/placa, validação de KM regressiva, motivo obrigatório em orçamento recusado, RBAC para `ADMIN` vs `ATENDENTE`) cobertas por testes automatizados de integração no backend.
  - Nenhuma complexidade desnecessária introduzida (sem filas distribuídas, microsserviços ou bancos externos no MVP).

## Project Structure

### Documentation (this feature)

```text
specs/001-crm-oficina-pesados/
├── plan.md              # Este arquivo
├── research.md          # Decisões técnicas (Phase 0)
├── data-model.md        # Modelo relacional e transições de estado (Phase 1)
├── quickstart.md        # Guia de execução e validação E2E (Phase 1)
├── contracts/
│   └── api-v1.md        # Contratos REST da API v1 (Phase 1)
└── tasks.md             # Gerado pelo /speckit-tasks (Phase 2)
```

### Source Code (repository root)

```text
backend/
├── alembic/
│   └── versions/
├── app/
│   ├── core/            # config, database (SQLite WAL/FK), security (JWT/RBAC)
│   ├── models/          # SQLAlchemy models (usuario, cliente, veiculo, orcamento, os, crm)
│   ├── schemas/         # Pydantic v2 request/response schemas
│   ├── services/        # Regras de negócio, conversão orçamento->OS, geração PDF, preventivas
│   ├── api/v1/          # Routers FastAPI (auth, clientes, veiculos, orcamentos, os, crm, dashboard)
│   ├── seed.py          # Usuários iniciais ADMIN e ATENDENTE
│   └── main.py          # Entrypoint FastAPI + CORS
├── data/                # crm.db (ignorado no git)
├── tests/               # pytest + httpx (auth, clientes, orcamentos, os, dashboard)
├── alembic.ini
└── requirements.txt

frontend/
├── src/
│   ├── app/             # App Router (login, dashboard, clientes/[id], orcamentos, os, lembretes, usuarios)
│   ├── components/      # UI compartilhada, Kanban, Checklist OS, Timeline, Busca Global
│   ├── lib/             # Cliente API tipado, auth context, helpers WhatsApp/formatação CNPJ-Placa
│   └── types/           # Tipos TypeScript alinhados aos contratos da API
├── package.json
└── tsconfig.json
```

**Structure Decision**: Estrutura separada `backend/` (FastAPI) e `frontend/` (Next.js App Router) na raiz do repositório `sdd-proj/`, mantendo contratos REST explícitos em `/api/v1` e documentação da feature em `specs/001-crm-oficina-pesados/`.

## Complexity Tracking

Nenhuma violação de constituição ou complexidade adicional que exija justificativa.
