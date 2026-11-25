# API Contracts (v1): CRM Oficina de Veículos de Grande Porte

**Base URL**: `/api/v1` | **Auth**: `Authorization: Bearer <jwt_token>`

---

## 1. Autenticação e Usuários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/auth/login` | Público | Autentica por `email` e `senha`, retorna `access_token` e dados do usuário (`id`, `nome`, `perfil`). |
| `GET` | `/auth/me` | Autenticado | Retorna perfil do usuário logado. |
| `GET` | `/usuarios` | `ADMIN` | Lista usuários internos. |
| `POST` | `/usuarios` | `ADMIN` | Cria usuário (`ADMIN` ou `ATENDENTE`). |
| `PATCH` | `/usuarios/{id}` | `ADMIN` | Atualiza perfil/status (`ativo: false` bloqueia login). |

---

## 2. Frotas (Clientes), Contatos, Motoristas e Veículos

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/busca?q={termo}` | Autenticado | Busca global por CNPJ, Razão Social, Nome Fantasia ou Placa. |
| `GET` | `/clientes` | Autenticado | Lista clientes paginados com filtros (`ativo`, `q`). |
| `POST` | `/clientes` | Autenticado | Cadastra cliente B2B (valida CNPJ único — `409 Conflict` se duplicado). |
| `GET` | `/clientes/{id}` | Autenticado | Retorna ficha completa (dados, contatos, motoristas, veículos, resumo de OS/orçamentos). |
| `PATCH` | `/clientes/{id}` | Autenticado | Atualiza dados cadastrais do cliente. |
| `POST` | `/clientes/{id}/contatos` | Autenticado | Adiciona contato à frota. |
| `PATCH` | `/contatos/{id}` | Autenticado | Atualiza contato. |
| `DELETE` | `/contatos/{id}` | Autenticado | Remove contato. |
| `POST` | `/clientes/{id}/motoristas` | Autenticado | Adiciona motorista à frota. |
| `PATCH` | `/motoristas/{id}` | Autenticado | Atualiza motorista. |
| `POST` | `/clientes/{id}/veiculos` | Autenticado | Cadastra veículo (valida placa única — `409 Conflict` se pertencer a outro cliente). |
| `PATCH` | `/veiculos/{id}` | Autenticado | Atualiza veículo (inclui transferência de `cliente_id` se confirmado). |

---

## 3. Orçamentos (Funil / Kanban) e PDF

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/orcamentos` | Autenticado | Lista orçamentos (suporta filtro por `etapa`, `cliente_id`, `veiculo_id`, período). |
| `POST` | `/orcamentos` | Autenticado | Cria orçamento com lista de itens (`PECA` / `SERVICO`), calculando totais. |
| `GET` | `/orcamentos/{id}` | Autenticado | Detalha orçamento e seus itens. |
| `PUT` | `/orcamentos/{id}` | Autenticado | Atualiza itens/desconto/observações (enquanto não convertido). |
| `PATCH` | `/orcamentos/{id}/etapa` | Autenticado | Move etapa no funil (`RASCUNHO`, `ENVIADO`, `EM_NEGOCIACAO`, `APROVADO`, `RECUSADO`). Exige `motivo_recusa` se `RECUSADO`. |
| `POST` | `/orcamentos/{id}/converter-os` | Autenticado | Converte orçamento `APROVADO` em OS (aceita dados iniciais de checklist de entrada). |
| `GET` | `/orcamentos/{id}/pdf` | Autenticado | Retorna `application/pdf` formatado do orçamento. |

---

## 4. Ordens de Serviço (OS)

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/ordens-servico` | Autenticado | Lista OS (filtros: `status`, `cliente_id`, `veiculo_id`). |
| `POST` | `/ordens-servico` | Autenticado | Abertura direta de OS com checklist de entrada. Valida `km_entrada < veiculo.km_atual` (retorna `422` se `confirmar_km_menor=false`). |
| `GET` | `/ordens-servico/{id}` | Autenticado | Detalha OS, itens, checklist entrada/saída e histórico de status. |
| `PATCH` | `/ordens-servico/{id}/status` | Autenticado | Atualiza status (`AGUARDANDO_PECA`, `EM_EXECUCAO`, `EM_TESTE`, `PRONTA`, `ENTREGUE`). Para `ENTREGUE`, exige dados de saída e permite agendar preventiva. |
| `POST` | `/ordens-servico/{id}/itens` | Autenticado | Adiciona item aditivo à OS em execução. |
| `GET` | `/ordens-servico/{id}/pdf` | Autenticado | Retorna `application/pdf` da OS. |

---

## 5. CRM: Timeline de Interações e Lembretes

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/clientes/{id}/interacoes` | Autenticado | Retorna timeline cronológica (manuais + eventos de sistema). |
| `POST` | `/clientes/{id}/interacoes` | Autenticado | Registra interação manual (`LIGACAO`, `WHATSAPP`, `EMAIL`, `PRESENCIAL`). |
| `GET` | `/lembretes` | Autenticado | Lista lembretes (`status=PENDENTE`, `ate_data`, `tipo`). |
| `POST` | `/lembretes` | Autenticado | Cria lembrete manual de `FOLLOW_UP` ou `PREVENTIVA`. |
| `PATCH` | `/lembretes/{id}` | Autenticado | Marca como `CONCLUIDO` ou reagenda (`REAGENDADO` + nova `data_prevista`). |

---

## 6. Painel Gerencial (Somente `ADMIN`)

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/dashboard/gerencial?inicio=&fim=` | `ADMIN` | Retorna KPIs do período: total orçado vs. aprovado, taxa de conversão (%), contagem de OS por status, valor total de OS entregues e ranking de motivos de recusa. |
