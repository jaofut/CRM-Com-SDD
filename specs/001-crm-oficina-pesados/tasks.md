---
description: "Task list for CRM Oficina de Veículos de Grande Porte"
---

# Tasks: CRM para Oficina de Veículos de Grande Porte

**Input**: Design documents from `/specs/001-crm-oficina-pesados/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/api-v1.md`, `quickstart.md`

**Tests**: Conforme Princípio III de `.specify/memory/constitution.md`, testes de integração (`pytest` + `httpx`) são incluídos para todas as regras críticas de negócio e RBAC.

**Organization**: Tarefas agrupadas por história de usuário (`US1` a `US5`) para permitir implementação e validação incremental.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos distintos, sem dependência pendente)
- **[Story]**: História de usuário correspondente (`US1`, `US2`, `US3`, `US4`, `US5`)
- Todos os caminhos são relativos à raiz `sdd-proj/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização da estrutura `backend/` (FastAPI) e `frontend/` (Next.js)

- [X] T001 Criar estrutura de diretórios `backend/app/` e `frontend/src/` conforme `plan.md`
- [X] T002 Inicializar projeto Python com FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PyJWT, bcrypt/pwdlib, ReportLab e pytest em `backend/requirements.txt`
- [X] T003 [P] Inicializar projeto Next.js (App Router) com TypeScript, Tailwind CSS, shadcn/ui e Lucide Icons em `frontend/package.json`
- [X] T004 [P] Configurar `.gitignore` para `backend/data/*.db`, `.venv/`, `frontend/.next/` e `node_modules/` na raiz de `sdd-proj/.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Banco SQLite, Alembic, segurança JWT/RBAC e layout base autenticável — bloqueia todas as histórias

**⚠️ CRITICAL**: Nenhuma história de usuário deve iniciar antes da conclusão desta fase

- [X] T005 Configurar settings e conexão SQLite (`PRAGMA foreign_keys=ON` e `WAL`) em `backend/app/core/config.py` e `backend/app/core/database.py`
- [X] T006 Configurar Alembic para migrations SQLite em `backend/alembic.ini` e `backend/alembic/env.py`
- [X] T007 [P] Criar modelo `Usuario` (`Usuario.nome`, `Usuario.email`, `Usuario.senha_hash`, `Usuario.perfil`, `Usuario.ativo` conforme `data-model.md`) em `backend/app/models/usuario.py`
- [X] T008 Implementar utilitários JWT, hash `bcrypt` e dependências `get_current_user` / `require_role` em `backend/app/core/security.py`
- [X] T009 [P] Implementar rotas `/api/v1/auth/login` e `/api/v1/auth/me` conforme `contracts/api-v1.md` em `backend/app/api/v1/auth.py`
- [X] T010 Criar entrypoint FastAPI com CORS e roteador `/api/v1` em `backend/app/main.py` e script `backend/app/seed.py`
- [X] T011 [P] Criar cliente HTTP tipado com gerenciamento de token JWT em `frontend/src/lib/api.ts` e tipos base em `frontend/src/types/auth.ts`
- [X] T012 [P] Implementar tela `/login` e layout autenticado com navegação lateral em `frontend/src/app/login/page.tsx` e `frontend/src/components/AppShell.tsx`

**Checkpoint**: Fundação pronta — login funcional, banco SQLite configurado e RBAC ativo no backend

---

## Phase 3: User Story 1 - Cadastro de Frotas, Contatos, Motoristas e Veículos (Priority: P1) 🎯 MVP

**Goal**: Permitir o cadastro completo de transportadoras B2B com contatos, motoristas e veículos pesados, além de busca global rápida por CNPJ, nome ou placa.

**Independent Test**: Cadastrar uma transportadora com CNPJ, 2 contatos, 1 motorista e 2 veículos; validar bloqueio de CNPJ/placa duplicados (`409`) e busca global em `< 2s`.

### Tests for User Story 1

- [X] T013 [P] [US1] Criar testes de integração para CRUD de clientes, unicidade de CNPJ/placa (`409`), transferência de veículo e busca global em `backend/tests/test_clientes_veiculos.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Criar modelos `Cliente` (`Cliente.razao_social`, `Cliente.nome_fantasia`, `Cliente.cnpj`, `Cliente.ativo`), `Contato` (`Contato.nome`, `Contato.cargo`, `Contato.telefone_whatsapp`, `Contato.principal`) e `Motorista` (`Motorista.nome`, `Motorista.ativo`) conforme `data-model.md` em `backend/app/models/cliente.py`
- [X] T015 [P] [US1] Criar modelo `Veiculo` (`Veiculo.placa`, `Veiculo.tipo`, `Veiculo.marca_modelo`, `Veiculo.km_atual`) conforme `data-model.md` em `backend/app/models/veiculo.py`
- [X] T016 [US1] Gerar migration Alembic inicial para `usuarios`, `clientes`, `contatos`, `motoristas` e `veiculos` em `backend/alembic/versions/`
- [X] T017 [P] [US1] Criar schemas Pydantic v2 de `Cliente`, `Contato`, `Motorista` e `Veiculo` em `backend/app/schemas/cliente.py` e `backend/app/schemas/veiculo.py`
- [X] T018 [US1] Implementar serviços de negócio (validação de CNPJ único, placa única e transferência de frota) em `backend/app/services/cliente_service.py` e `backend/app/services/veiculo_service.py`
- [X] T019 [US1] Implementar endpoints `/clientes`, `/contatos`, `/motoristas`, `/veiculos` e `/busca` conforme `contracts/api-v1.md` em `backend/app/api/v1/clientes.py` e `backend/app/api/v1/veiculos.py`
- [X] T020 [P] [US1] Criar barra de busca global e listagem/cadastro de frotas em `frontend/src/components/GlobalSearch.tsx` e `frontend/src/app/clientes/page.tsx`
- [X] T021 [US1] Criar ficha completa do cliente (abas Contatos, Motoristas e Veículos) em `frontend/src/app/clientes/[id]/page.tsx`

**Checkpoint**: User Story 1 funcional e testável de forma independente

---

## Phase 4: User Story 2 - Funil Visual de Orçamentos e Geração de PDF (Priority: P1)

**Goal**: Gerenciar orçamentos em funil Kanban (`Rascunho` → `Enviado` → `Em Negociação` → `Aprovado`/`Recusado`), gerar PDF, abrir atalho WhatsApp Web e converter orçamento aprovado em OS.

**Independent Test**: Criar orçamento com peças e serviços, gerar PDF, mover para `Recusado` validando motivo obrigatório, e converter orçamento `Aprovado` em OS.

### Tests for User Story 2

- [X] T022 [P] [US2] Criar testes de integração para cálculo de totais, motivo obrigatório em `RECUSADO` e geração de PDF em `backend/tests/test_orcamentos.py`

### Implementation for User Story 2

- [X] T023 [P] [US2] Criar modelos `Orcamento` (`Orcamento.numero`, `Orcamento.etapa`, `Orcamento.validade_dias`, `Orcamento.desconto_total`, `Orcamento.motivo_recusa`, `Orcamento.po_aprovacao`, `Orcamento.valor_total`) e `OrcamentoItem` (`OrcamentoItem.tipo`, `OrcamentoItem.descricao`, `OrcamentoItem.quantidade`, `OrcamentoItem.valor_unitario`, `OrcamentoItem.subtotal`) conforme `data-model.md` em `backend/app/models/orcamento.py`
- [X] T024 [US2] Gerar migration Alembic para `orcamentos` e `orcamento_itens` em `backend/alembic/versions/`
- [X] T025 [P] [US2] Criar schemas Pydantic v2 de `Orcamento` e `OrcamentoItem` em `backend/app/schemas/orcamento.py`
- [X] T026 [US2] Implementar serviço de orçamentos (numeração sequencial, cálculo de totais, transições de etapa e validação de `Orcamento.motivo_recusa`) em `backend/app/services/orcamento_service.py`
- [X] T027 [P] [US2] Implementar gerador de PDF de orçamento com ReportLab em `backend/app/services/pdf_service.py`
- [X] T028 [US2] Implementar endpoints `/orcamentos`, `/orcamentos/{id}/etapa` e `/orcamentos/{id}/pdf` conforme `contracts/api-v1.md` em `backend/app/api/v1/orcamentos.py`
- [X] T029 [P] [US2] Criar funil Kanban de orçamentos, modal de novo orçamento/itens e botão de atalho WhatsApp Web (`wa.me`) em `frontend/src/app/orcamentos/page.tsx` e `frontend/src/components/OrcamentoKanban.tsx`

**Checkpoint**: User Story 2 funcional (nota: endpoint `/converter-os` integra-se com o modelo `OrdemServico` da US3 na próxima fase)

---

## Phase 5: User Story 3 - Ordem de Serviço (OS) com Checklist de Entrada/Saída e Acompanhamento (Priority: P1)

**Goal**: Abrir OS (direta ou convertida de orçamento aprovado), registrar checklist de entrada/saída, validar KM regressiva, atualizar status até `Entregue` e gerar PDF da OS.

**Independent Test**: Converter orçamento em OS, testar bloqueio de KM menor sem confirmação, avançar status até `Entregue` com motorista de saída e gerar PDF da OS.

### Tests for User Story 3

- [X] T030 [P] [US3] Criar testes de integração para conversão Orçamento → OS, validação de KM regressiva (`confirmar_km_menor`), transição para `ENTREGUE` e geração de PDF da OS em `backend/tests/test_ordens_servico.py`

### Implementation for User Story 3

- [X] T031 [P] [US3] Criar modelos `OrdemServico` (`OrdemServico.numero`, `OrdemServico.status`, `OrdemServico.km_entrada`, `OrdemServico.confirmar_km_menor`, `OrdemServico.motorista_saida_id`, `OrdemServico.valor_total`, `OrdemServico.data_entrada`), `OrdemServicoItem` (`OrdemServicoItem.tipo`, `OrdemServicoItem.descricao`, `OrdemServicoItem.quantidade`, `OrdemServicoItem.valor_unitario`, `OrdemServicoItem.subtotal`) e `OrdemServicoHistorico` (`OrdemServicoHistorico.status_novo`, `OrdemServicoHistorico.created_at`) conforme `data-model.md` em `backend/app/models/ordem_servico.py`
- [X] T032 [US3] Gerar migration Alembic para `ordens_servico`, `ordem_servico_itens` e `ordem_servico_historico` em `backend/alembic/versions/`
- [X] T033 [P] [US3] Criar schemas Pydantic v2 de `OrdemServico`, checklist e histórico em `backend/app/schemas/ordem_servico.py`
- [X] T034 [US3] Implementar serviço de OS (conversão integral de orçamento, validação de `OrdemServico.km_entrada` vs `Veiculo.km_atual`, histórico de status e atualização de `Veiculo.km_atual`) em `backend/app/services/os_service.py`
- [X] T035 [US3] Estender `backend/app/services/pdf_service.py` para gerar PDF da OS finalizada e conectar `POST /orcamentos/{id}/converter-os` em `backend/app/api/v1/orcamentos.py`
- [X] T036 [US3] Implementar endpoints `/ordens-servico`, `/ordens-servico/{id}/status`, `/ordens-servico/{id}/itens` e `/ordens-servico/{id}/pdf` conforme `contracts/api-v1.md` em `backend/app/api/v1/ordens_servico.py`
- [X] T037 [P] [US3] Criar painel de OS em aberto, tela de detalhe com checklist de entrada/saída e modal de confirmação de KM menor em `frontend/src/app/os/page.tsx` e `frontend/src/app/os/[id]/page.tsx`

**Checkpoint**: Fluxo completo MVP (US1 + US2 + US3) operacional de ponta a ponta

---

## Phase 6: User Story 4 - Timeline de Interações e Lembretes de Manutenção Preventiva (Priority: P2)

**Goal**: Registrar timeline cronológica por cliente (interações manuais + eventos de sistema) e gerenciar lembretes de follow-up e manutenção preventiva gerados na entrega da OS.

**Independent Test**: Registrar interação manual na ficha do cliente, concluir uma OS verificando geração automática de lembrete preventivo e concluir/reagendar o lembrete na fila diária.

### Tests for User Story 4

- [X] T038 [P] [US4] Criar testes de integração para timeline de interações e criação/conclusão de lembretes preventivos em `backend/tests/test_crm_lembretes.py`

### Implementation for User Story 4

- [X] T039 [P] [US4] Criar modelos `Interacao` (`Interacao.tipo`, `Interacao.resumo`) e `Lembrete` (`Lembrete.tipo`, `Lembrete.titulo`, `Lembrete.data_prevista`, `Lembrete.km_previsto`, `Lembrete.status`) conforme `data-model.md` em `backend/app/models/crm.py`
- [X] T040 [US4] Gerar migration Alembic para `interacoes` e `lembretes` em `backend/alembic/versions/`
- [X] T041 [P] [US4] Criar schemas Pydantic v2 de `Interacao` e `Lembrete` em `backend/app/schemas/crm.py`
- [X] T042 [US4] Implementar serviços de timeline e agendamento automático de preventiva na entrega da OS em `backend/app/services/crm_service.py` e integrar gancho em `backend/app/services/os_service.py`
- [X] T043 [US4] Implementar endpoints `/clientes/{id}/interacoes` e `/lembretes` conforme `contracts/api-v1.md` em `backend/app/api/v1/crm.py`
- [X] T044 [P] [US4] Integrar aba Timeline na ficha do cliente (`frontend/src/components/ClienteTimeline.tsx`) e criar tela "Follow-ups e Preventivas" em `frontend/src/app/lembretes/page.tsx`

**Checkpoint**: User Story 4 funcional e integrada à entrega de OS

---

## Phase 7: User Story 5 - Controle de Acesso (2 Perfis) e Painel Gerencial (Priority: P2)

**Goal**: Permitir ao `ADMIN` gerenciar usuários (`ADMIN` / `ATENDENTE`, ativar/desativar preservando histórico) e visualizar KPIs gerenciais no dashboard.

**Independent Test**: Validar que `ATENDENTE` recebe `403 Forbidden` em `/usuarios` e `/dashboard/gerencial`, e que `ADMIN` visualiza taxa de conversão, OS por status e motivos de recusa.

### Tests for User Story 5

- [X] T045 [P] [US5] Criar testes de integração de RBAC (`403` para `ATENDENTE`, login bloqueado para `Usuario.ativo=False`) e KPIs do dashboard em `backend/tests/test_usuarios_dashboard.py`

### Implementation for User Story 5

- [X] T046 [P] [US5] Criar schemas Pydantic v2 de gestão de usuários e KPIs gerenciais em `backend/app/schemas/usuario.py` e `backend/app/schemas/dashboard.py`
- [X] T047 [US5] Implementar endpoints `/usuarios` (`ADMIN`) e `/dashboard/gerencial` (`ADMIN`) conforme `contracts/api-v1.md` em `backend/app/api/v1/usuarios.py` e `backend/app/api/v1/dashboard.py`
- [X] T048 [P] [US5] Criar páginas `/dashboard` (KPIs e gráficos/tabelas) e `/usuarios` (somente `ADMIN`) em `frontend/src/app/dashboard/page.tsx` e `frontend/src/app/usuarios/page.tsx`

**Checkpoint**: Todas as 5 histórias de usuário completas e protegidas por RBAC

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validação final, qualidade de código e execução completa do `quickstart.md`

- [X] T049 [P] Executar suíte completa `pytest` no backend, `npm run typecheck` e `npm test` (Vitest) no frontend corrigindo eventuais avisos
- [X] T050 Executar todos os 5 cenários E2E descritos em `specs/001-crm-oficina-pesados/quickstart.md` e validar geração de PDFs

---

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)** → bloqueia todas as histórias.
- **US1 (Phase 3)** → base para **US2 (Phase 4)** e **US3 (Phase 5)** (orçamentos e OS dependem de Cliente e Veículo).
- **US2 (Phase 4)** e **US3 (Phase 5)** → conversão `/orcamentos/{id}/converter-os` conecta ambas na Phase 5.
- **US4 (Phase 6)** → usa `Cliente`, `Veiculo` (US1) e gancho opcional na entrega da `OrdemServico` (US3).
- **US5 (Phase 7)** → agrega dados de Orçamentos (US2) e OS (US3) para o dashboard `ADMIN`.
- **Polish (Phase 8)** → executa após todas as fases desejadas.

## Implementation Strategy

- **MVP Inicial (Fases 1 a 5 — T001 a T037)**: Entrega o ciclo operacional completo (Login → Cadastro de Frota/Veículos → Funil de Orçamentos + PDF → OS com Checklist + PDF).
- **Incremento CRM & Gestão (Fases 6 a 8 — T038 a T050)**: Adiciona Timeline, Preventivas e Painel Gerencial `ADMIN`.
