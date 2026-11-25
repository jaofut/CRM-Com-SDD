<!--
Sync Impact Report
- Version change: template (uninitialized) -> 1.0.0
- Modified principles:
  - [PRINCIPLE_1_NAME] -> I. Separação Clara de Camadas (API, Domínio e UI)
  - [PRINCIPLE_2_NAME] -> II. Integridade de Dados e Rastreabilidade B2B
  - [PRINCIPLE_3_NAME] -> III. Testes Automatizados para Regras Críticas
  - [PRINCIPLE_4_NAME] -> IV. Simplicidade Pragmática (YAGNI)
  - [PRINCIPLE_5_NAME] -> V. Segurança e Controle de Acesso (RBAC)
- Added sections:
  - Stack Tecnológica e Restrições Operacionais
  - Fluxo de Desenvolvimento e Qualidade
- Removed sections: None
- Follow-up TODOs: None
-->
# CRM Oficina Pesados Constitution

## Core Principles

### I. Separação Clara de Camadas (API, Domínio e UI)

O backend FastAPI MUST manter separação estrita entre rotas HTTP (`api/v1/`), contratos de entrada/saída (`schemas/`), regras de negócio (`services/`) e persistência (`models/`). O frontend Next.js MUST comunicar-se exclusivamente via API REST `/api/v1`, sem acesso direto ao banco SQLite.

### II. Integridade de Dados e Rastreabilidade B2B

O banco SQLite MUST operar com `PRAGMA foreign_keys=ON` e `WAL` mode habilitados. Regras de unicidade (CNPJ de clientes e placa de veículos) MUST ser garantidas tanto na camada de serviço quanto por restrições no banco. Registros históricos (orçamentos aprovados, OS, interações e autoria de usuários desativados) MUST NOT ser excluídos fisicamente.

### III. Testes Automatizados para Regras Críticas

Toda regra de negócio crítica — controle de acesso (`ADMIN` vs `ATENDENTE`), bloqueio de CNPJ/placa duplicados, alerta de KM regressiva, motivo obrigatório em orçamento recusado e conversão integral de Orçamento em OS — MUST possuir testes automatizados de integração com `pytest` e `httpx` passando antes da conclusão da tarefa.

### IV. Simplicidade Pragmática (YAGNI)

O MVP MUST permanecer autocontido e operável em rede local/desktop sem serviços externos obrigatórios (sem API paga de WhatsApp, emissão de NF-e ou servidor de banco externo). Qualquer nova abstração, fila assíncrona ou dependência estrutural MUST ser justificada na seção Complexity Tracking do `plan.md`.

### V. Segurança e Controle de Acesso (RBAC)

Todas as rotas de negócio MUST exigir autenticação via JWT válido, com senhas armazenadas exclusivamente com hash seguro (`bcrypt`). A restrição de acesso entre `ADMIN` e `ATENDENTE` MUST ser aplicada no backend em cada endpoint protegido, nunca dependendo apenas de ocultação de interface no frontend.

## Stack Tecnológica e Restrições Operacionais

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic e SQLite local (`backend/data/crm.db`).
- **Geração de Documentos**: PDFs de Orçamentos e OS MUST usar biblioteca pure-Python (ReportLab) para garantir execução nativa em Windows e Linux sem binários externos.
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS e componentes shadcn/ui.

## Fluxo de Desenvolvimento e Qualidade

- O ciclo Spec-Driven Development (`spec.md` → `plan.md` → `tasks.md` → implementação) MUST ser seguido para todas as features.
- Toda alteração no modelo de dados MUST ser acompanhada de migration versionada via Alembic (`alembic upgrade head`).
- Antes de encerrar qualquer tarefa de implementação, `pytest` (backend) e `tsc --noEmit` (frontend) MUST executar sem erros.

## Governance

Esta Constituição prevalece sobre decisões ad-hoc durante o desenvolvimento. Alterações nos princípios exigem atualização versionada deste arquivo seguindo versionamento semântico (`MAJOR` para remoção/redefinição incompatível, `MINOR` para novos princípios ou expansões materiais, `PATCH` para ajustes editoriais) e revisão de impacto em `plan.md` e `tasks.md`.

**Version**: 1.0.0 | **Ratified**: 2026-11-24 | **Last Amended**: 2026-11-24
