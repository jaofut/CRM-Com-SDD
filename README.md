# CRM para Oficina de Veículos de Grande Porte

Sistema web de CRM focado em oficinas de veículos pesados (caminhões, carretas e ônibus) para atendimento de frotas e transportadoras B2B, construído com **Spec-Driven Development (SDD)** usando o **Spec Kit**.

---

## Estrutura dos Artefatos SDD

Todos os documentos de especificação e planejamento estão em [`specs/001-crm-oficina-pesados/`](specs/001-crm-oficina-pesados/).

### 1. [`spec.md`](specs/001-crm-oficina-pesados/spec.md) — Especificação Funcional
Define **o quê** o sistema faz e **por quê**, sem amarras de tecnologia. Seus subtópicos são:
- **User Scenarios & Testing**: 5 histórias de usuário priorizadas e testáveis de forma independente (com cenários *Given / When / Then*):
  - **US1 (P1)**: Cadastro de Frotas, Contatos, Motoristas e Veículos (+ busca global).
  - **US2 (P1)**: Funil Visual de Orçamentos (Kanban), Geração de PDF e atalho WhatsApp Web.
  - **US3 (P1)**: Ordem de Serviço (OS) com Checklist de Entrada/Saída e Acompanhamento.
  - **US4 (P2)**: Timeline de Interações e Lembretes de Manutenção Preventiva.
  - **US5 (P2)**: Controle de Acesso (2 Perfis: `Administrador/Gerente` e `Atendente/Consultor`) e Painel Gerencial.
- **Edge Cases**: Tratamento de CNPJ duplicado, transferência de placa entre frotas, KM regressiva na entrada da OS, alterações após aprovação do orçamento e desativação de usuário preservando histórico.
- **Requirements**:
  - **Functional Requirements (`FR-001` a `FR-014`)**: Regras detalhadas de autenticação/RBAC no servidor, unicidade, funil, PDF, checklist, preventivas e inativação lógica.
  - **Key Entities**: `Usuário`, `Cliente`, `Contato`, `Motorista`, `Veículo`, `Orçamento`, `Ordem de Serviço (OS)`, `Interação` e `Lembrete / Preventiva`.
- **Success Criteria (`SC-001` a `SC-005`)**: Métricas mensuráveis (ex.: cadastro + primeiro PDF em `< 4 min`, busca por placa/CNPJ em `< 2s`).
- **Assumptions**: Escopo B2B, mecânicos não operam o sistema diretamente e exclusão de integrações externas na v1 (sem NF-e, API oficial do WhatsApp, estoque completo ou financeiro).

### 2. [`plan.md`](specs/001-crm-oficina-pesados/plan.md) — Plano de Implementação
Define **como** a especificação é traduzida em arquitetura e código. Seus subtópicos são:
- **Summary**: Visão geral da arquitetura adotada para o CRM.
- **Technical Context**:
  - **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PyJWT, bcrypt e ReportLab (PDF nativo no Windows/Linux).
  - **Storage**: SQLite local (`backend/data/crm.db`) com `PRAGMA foreign_keys=ON` e `WAL` mode.
  - **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS e Lucide Icons.
  - **Testing**: `pytest` + `httpx` no backend; `tsc --noEmit` + `Vitest` no frontend.
- **Constitution Check**: Validação dos 5 princípios da [constituição do projeto](.specify/memory/constitution.md) (separação de camadas, integridade B2B, testes automatizados em regras críticas, YAGNI e RBAC no backend).
- **Project Structure**: Árvore de diretórios de documentação (`research.md`, `data-model.md`, `contracts/api-v1.md`, `quickstart.md`) e código-fonte (`backend/` e `frontend/`).
- **Complexity Tracking**: Registro de justificativas caso haja desvios de simplicidade (nenhum desvio neste projeto).

### 3. [`tasks.md`](specs/001-crm-oficina-pesados/tasks.md) — Plano de Tarefas Executáveis
Quebra o plano e o modelo de dados em **50 tarefas** (`T001` a `T050`) ordenadas por dependência, com marcadores `[P]` (paralelizáveis), `[USx]` (história vinculada), caminhos exatos de arquivos e citações explícitas `Entity.field` de `data-model.md`:
- **Phase 1 — Setup (`T001`–`T004`)**: Estrutura `backend/` e `frontend/`, dependências e `.gitignore`.
- **Phase 2 — Foundational (`T005`–`T012`)**: SQLite (`WAL`/`FK`), Alembic, `Usuario`, JWT/RBAC, cliente HTTP e `AppShell`.
- **Phase 3 — US1 (`T013`–`T021`)**: Modelos, serviços, endpoints, testes e telas de Frotas, Contatos, Motoristas, Veículos e Busca Global.
- **Phase 4 — US2 (`T022`–`T029`)**: Modelos, cálculo, motivo de recusa, PDF ReportLab, testes e Kanban de Orçamentos.
- **Phase 5 — US3 (`T030`–`T037`)**: Modelos de OS, conversão Orçamento → OS, validação de KM regressiva, checklist entrada/saída, PDF da OS, testes e telas de OS.
- **Phase 6 — US4 (`T038`–`T044`)**: Timeline de interações, agendamento automático de preventiva na entrega da OS, testes e tela de Lembretes.
- **Phase 7 — US5 (`T045`–`T048`)**: Gestão de usuários e painel gerencial (`ADMIN`), com testes de `403 Forbidden` para `ATENDENTE`.
- **Phase 8 — Polish (`T049`–`T050`)**: Execução completa de `pytest`, `typecheck`, `vitest` e validação E2E do `quickstart.md`.
- **Dependencies & Execution Order / Implementation Strategy**: Ordem de bloqueio entre fases e corte de MVP inicial (Fases 1 a 5).

---

## Fluxo de Comandos Utilizado

O projeto foi conduzido seguindo a sequência abaixo:

```text
/grill-me ──▶ speckit-plan ──▶ speckit-constitution ──▶ revisão do spec.md ──▶ speckit-tasks ──▶ speckit-analyze ──▶ speckit-implement
```

1. **`/grill-me`**: Entrevista guiada pergunta a pergunta para fechar escopo, público B2B, 2 perfis de acesso, fluxo Kanban → OS, checklist, preventivas e limites da v1, gerando o [`spec.md`](specs/001-crm-oficina-pesados/spec.md).
2. **`speckit-plan`**: Definição da stack (`FastAPI + SQLite + Next.js`) e geração do [`plan.md`](specs/001-crm-oficina-pesados/plan.md), [`research.md`](specs/001-crm-oficina-pesados/research.md), [`data-model.md`](specs/001-crm-oficina-pesados/data-model.md), [`contracts/api-v1.md`](specs/001-crm-oficina-pesados/contracts/api-v1.md) e [`quickstart.md`](specs/001-crm-oficina-pesados/quickstart.md).
3. **`speckit-constitution`**: Ratificação da [`constitution.md`](.specify/memory/constitution.md) (`v1.0.0`) com os princípios técnicos e de governança do projeto, seguida do alinhamento pontual de `FR-001` e `FR-014` no `spec.md`.
4. **`speckit-tasks`**: Geração do [`tasks.md`](specs/001-crm-oficina-pesados/tasks.md) com as 50 tarefas organizadas por fase e história de usuário.
5. **`speckit-analyze`**: Auditoria cruzada (somente leitura) entre `spec.md`, `plan.md`, `data-model.md`, `tasks.md` e `constitution.md`, identificando 4 melhorias (`F1`, `I1`, `A1`, `U1`) que foram aplicadas antes da codificação.
6. **`speckit-implement`**: Execução das 50 tarefas, geração da migration inicial no Alembic, seed de usuários, implementação completa de backend e frontend e validação dos testes (`5 passed` no `pytest`, `0` erros no `tsc --noEmit` e `2 passed` no `Vitest`).

---

## Como Executar Localmente

### Backend (FastAPI + SQLite)
```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
- Swagger UI: `http://localhost:8000/docs`

### Frontend (Next.js)
```powershell
cd frontend
npm run dev
```
- Aplicação web: `http://localhost:3000`
- Usuários iniciais (seed): `admin@oficina.com` / `admin123` (`ADMIN`) e `atendente@oficina.com` / `atendente123` (`ATENDENTE`).

### Testes
```powershell
# Backend
cd backend
.\.venv\Scripts\pytest.exe -v

# Frontend
cd frontend
npm run typecheck
npm test
```
