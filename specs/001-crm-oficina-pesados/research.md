# Phase 0 Research: CRM para Oficina de Veículos de Grande Porte

**Feature**: `001-crm-oficina-pesados` | **Date**: 2026-11-24

## Decisões Técnicas

### 1. Backend API & ORM
- **Decision**: Python 3.11+ com **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0** e **Alembic** para migrations.
- **Rationale**: FastAPI oferece validação automática de contratos via Pydantic, geração nativa de OpenAPI/Swagger (`/docs`) e excelente produtividade para APIs REST tipadas. SQLAlchemy 2.0 + Alembic garante modelagem relacional limpa e evoluções de schema controladas.
- **Alternatives considered**:
  - *Django + DRF*: Mais pesado para o escopo focado do MVP e menos direto na separação de schemas OpenAPI puros.
  - *SQLModel*: Bom, mas SQLAlchemy 2.0 puro oferece maior maturidade para relacionamentos complexos e migrations com Alembic.

### 2. Banco de Dados Local
- **Decision**: **SQLite** local (`backend/data/crm.db`) com `PRAGMA journal_mode=WAL` e `PRAGMA foreign_keys=ON` habilitados na conexão.
- **Rationale**: Atende perfeitamente ao requisito de rodar localmente sem servidor de banco dedicado no MVP, mantendo integridade referencial estrita (`foreign_keys=ON`) e boa concorrência de leitura/escrita com `WAL`. A camada SQLAlchemy facilita migração futura para PostgreSQL se a oficina crescer para múltiplas filiais.
- **Alternatives considered**:
  - *PostgreSQL*: Exigiria setup de container/serviço externo já no MVP.

### 3. Autenticação e Controle de Acesso (RBAC)
- **Decision**: Autenticação via **JWT** (token de acesso assinado com `PyJWT`) e hash de senha com **bcrypt** (`pwdlib` / `passlib`), com dependência FastAPI `require_role(["ADMIN", "ATENDENTE"])`.
- **Rationale**: Simples, stateless e fácil de integrar tanto com o frontend Next.js quanto com testes automatizados via `pytest` (`httpx`). Cobre exatamente os 2 perfis definidos na spec (`Administrador/Gerente` e `Atendente/Consultor`).
- **Alternatives considered**:
  - *Sessão server-side em banco*: Adiciona tabela e limpeza de sessões sem ganho real para 2 perfis internos.

### 4. Geração de PDF (Orçamentos e OS)
- **Decision**: Biblioteca **ReportLab** (ou **fpdf2**), 100% Python, rodando no backend via endpoints `/orcamentos/{id}/pdf` e `/os/{id}/pdf`.
- **Rationale**: Funciona nativamente no Windows e Linux sem exigir binários externos (GTK/Cairo/Chromium), evitando problemas de instalação no ambiente local do usuário.
- **Alternatives considered**:
  - *WeasyPrint*: Exige bibliotecas nativas GTK/Pango no Windows, o que costuma gerar atrito de setup.
  - *Playwright/Puppeteer*: Pesado demais apenas para gerar PDFs simples de orçamento e OS.

### 5. Frontend & Kanban de Orçamentos
- **Decision**: **Next.js (App Router)** com **TypeScript**, **Tailwind CSS** e componentes **shadcn/ui** (Radix UI + Lucide Icons), consumindo a API FastAPI via cliente HTTP tipado (`fetch`).
- **Rationale**: Permite construir rapidamente interfaces ricas de CRM (busca global, ficha do cliente com abas de veículos/contatos/timeline, Kanban de orçamentos com drag-and-drop ou troca rápida de etapa e formulários de checklist de OS).
- **Alternatives considered**:
  - *React + Vite puro*: Também viável, mas Next.js App Router organiza melhor rotas de app, layouts autenticados e tipagem.

### 6. Atalho WhatsApp Web e Lembretes Preventivos
- **Decision**:
  - **WhatsApp Web**: Geração de link `https://wa.me/55{telefone}?text={mensagem_codificada}` no frontend usando o telefone do contato selecionado.
  - **Preventivas**: Cálculo automático de `data_prevista` (ex.: `+90 dias` padrão ou configurável) e `km_previsto_opcional` no momento em que a OS passa para `Entregue`, sem depender de daemon externo de fila.
- **Rationale**: Cumpre 100% do escopo da v1 sem integrações externas complexas, mantendo o fluxo rápido e confiável.
- **Alternatives considered**:
  - *Celery/Redis para agendamento*: Complexidade desnecessária quando os lembretes são consultados na fila diária do atendente via query SQL por `data_prevista <= hoje + janela`.
