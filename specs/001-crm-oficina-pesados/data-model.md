# Data Model: CRM para Oficina de Veículos de Grande Porte

**Feature**: `001-crm-oficina-pesados` | **Storage**: SQLite (via SQLAlchemy 2.0 + Alembic)

## Entidades e Relacionamentos

```text
Usuario (1) ──< (N) Interacao
Cliente (1) ──< (N) Contato
Cliente (1) ──< (N) Motorista
Cliente (1) ──< (N) Veiculo
Cliente (1) ──< (N) Orcamento
Cliente (1) ──< (N) OrdemServico
Cliente (1) ──< (N) Interacao
Cliente (1) ──< (N) Lembrete
Veiculo (1) ──< (N) Orcamento
Veiculo (1) ──< (N) OrdemServico
Orcamento (1) ──< (N) OrcamentoItem
Orcamento (0..1) ── (0..1) OrdemServico
OrdemServico (1) ──< (N) OrdemServicoItem
OrdemServico (1) ──< (N) OrdemServicoHistorico
```

---

### 1. `usuarios`
- `id`: INTEGER PK
- `nome`: VARCHAR(120) NOT NULL
- `email`: VARCHAR(150) UNIQUE NOT NULL
- `senha_hash`: VARCHAR(255) NOT NULL
- `perfil`: ENUM(`ADMIN`, `ATENDENTE`) NOT NULL
- `ativo`: BOOLEAN NOT NULL DEFAULT TRUE
- `created_at`: DATETIME NOT NULL

**Regras**: Usuário com `ativo = False` é impedido de autenticar, mas permanece referenciado em registros históricos.

---

### 2. `clientes` (Frotas / Transportadoras B2B)
- `id`: INTEGER PK
- `razao_social`: VARCHAR(180) NOT NULL
- `nome_fantasia`: VARCHAR(180) NOT NULL
- `cnpj`: VARCHAR(18) UNIQUE NOT NULL (armazenado normalizado ou formatado com validação de unicidade)
- `inscricao_estadual`: VARCHAR(30) NULL
- `endereco`: TEXT NULL
- `condicoes_comerciais`: TEXT NULL (ex.: prazo de faturamento, forma de pagamento)
- `observacoes`: TEXT NULL
- `ativo`: BOOLEAN NOT NULL DEFAULT TRUE
- `created_at`: DATETIME NOT NULL
- `updated_at`: DATETIME NOT NULL

**Regras**: CNPJ único entre clientes cadastrados; busca global indexada por `cnpj`, `razao_social` e `nome_fantasia`.

---

### 3. `contatos`
- `id`: INTEGER PK
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `nome`: VARCHAR(120) NOT NULL
- `cargo`: VARCHAR(80) NOT NULL (ex.: Gestor de Frota, Financeiro, Comprador)
- `telefone_whatsapp`: VARCHAR(30) NOT NULL
- `email`: VARCHAR(150) NULL
- `principal`: BOOLEAN NOT NULL DEFAULT FALSE

---

### 4. `motoristas`
- `id`: INTEGER PK
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `nome`: VARCHAR(120) NOT NULL
- `telefone`: VARCHAR(30) NULL
- `documento`: VARCHAR(30) NULL (CPF/CNH opcional)
- `ativo`: BOOLEAN NOT NULL DEFAULT TRUE

---

### 5. `veiculos`
- `id`: INTEGER PK
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `placa`: VARCHAR(10) UNIQUE NOT NULL (normalizada em maiúsculas sem hífen, ex.: `ABC1D23`)
- `tipo`: ENUM(`CAVALO_MECANICO`, `CARRETA`, `TRUCK`, `TOCO`, `ONIBUS`, `UTILITARIO_PESADO`, `OUTRO`) NOT NULL
- `marca_modelo`: VARCHAR(120) NOT NULL
- `ano`: INTEGER NULL
- `chassi`: VARCHAR(30) NULL
- `km_atual`: INTEGER NOT NULL DEFAULT 0
- `updated_at`: DATETIME NOT NULL

**Regras**:
- Placa única no sistema. Caso já exista em outra frota, o fluxo de transferência atualiza `cliente_id` preservando o histórico ou registrando evento na timeline.
- `km_atual` é atualizado automaticamente quando uma OS registra `km_entrada >= km_atual` (ou confirmado manualmente caso haja troca de painel).

---

### 6. `orcamentos`
- `id`: INTEGER PK
- `numero`: VARCHAR(20) UNIQUE NOT NULL (ex.: `ORC-2026-0001`)
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `contato_id`: INTEGER FK -> `contatos.id` NOT NULL
- `veiculo_id`: INTEGER FK -> `veiculos.id` NOT NULL
- `usuario_id`: INTEGER FK -> `usuarios.id` NOT NULL
- `etapa`: ENUM(`RASCUNHO`, `ENVIADO`, `EM_NEGOCIACAO`, `APROVADO`, `RECUSADO`) NOT NULL DEFAULT `RASCUNHO`
- `validade_dias`: INTEGER NOT NULL DEFAULT 15
- `desconto_total`: DECIMAL(12,2) NOT NULL DEFAULT 0
- `valor_total`: DECIMAL(12,2) NOT NULL DEFAULT 0
- `po_aprovacao`: VARCHAR(60) NULL (nº Pedido de Compra / aprovação)
- `motivo_recusa`: VARCHAR(200) NULL (obrigatório quando `etapa == RECUSADO`)
- `observacoes`: TEXT NULL
- `created_at`: DATETIME NOT NULL
- `updated_at`: DATETIME NOT NULL

#### `orcamento_itens`
- `id`: INTEGER PK
- `orcamento_id`: INTEGER FK -> `orcamentos.id` ON DELETE CASCADE
- `tipo`: ENUM(`PECA`, `SERVICO`) NOT NULL
- `descricao`: VARCHAR(200) NOT NULL
- `quantidade`: DECIMAL(10,2) NOT NULL
- `valor_unitario`: DECIMAL(12,2) NOT NULL
- `subtotal`: DECIMAL(12,2) NOT NULL

**Transições de Estado (`Orçamento`)**:
```text
RASCUNHO -> ENVIADO -> EM_NEGOCIACAO -> APROVADO -> (gera OrdemServico)
                  \                 \-> RECUSADO (exige motivo_recusa)
                   \-> APROVADO
                   \-> RECUSADO
```

---

### 7. `ordens_servico`
- `id`: INTEGER PK
- `numero`: VARCHAR(20) UNIQUE NOT NULL (ex.: `OS-2026-0001`)
- `orcamento_id`: INTEGER FK -> `orcamentos.id` NULL
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `veiculo_id`: INTEGER FK -> `veiculos.id` NOT NULL
- `usuario_abertura_id`: INTEGER FK -> `usuarios.id` NOT NULL
- `status`: ENUM(`AGUARDANDO_PECA`, `EM_EXECUCAO`, `EM_TESTE`, `PRONTA`, `ENTREGUE`) NOT NULL DEFAULT `AGUARDANDO_PECA`
- `km_entrada`: INTEGER NOT NULL
- `confirmar_km_menor`: BOOLEAN NOT NULL DEFAULT FALSE
- `motorista_entrada_id`: INTEGER FK -> `motoristas.id` NULL
- `avarias_entrada`: TEXT NULL
- `motorista_saida_id`: INTEGER FK -> `motoristas.id` NULL
- `observacoes_saida`: TEXT NULL
- `valor_total`: DECIMAL(12,2) NOT NULL DEFAULT 0
- `data_entrada`: DATETIME NOT NULL
- `data_entrega`: DATETIME NULL

#### `ordem_servico_itens`
- `id`: INTEGER PK
- `os_id`: INTEGER FK -> `ordens_servico.id` ON DELETE CASCADE
- `tipo`: ENUM(`PECA`, `SERVICO`) NOT NULL
- `descricao`: VARCHAR(200) NOT NULL
- `quantidade`: DECIMAL(10,2) NOT NULL
- `valor_unitario`: DECIMAL(12,2) NOT NULL
- `subtotal`: DECIMAL(12,2) NOT NULL

#### `ordem_servico_historico`
- `id`: INTEGER PK
- `os_id`: INTEGER FK -> `ordens_servico.id` ON DELETE CASCADE
- `status_anterior`: VARCHAR(30) NULL
- `status_novo`: VARCHAR(30) NOT NULL
- `usuario_id`: INTEGER FK -> `usuarios.id` NOT NULL
- `observacao`: TEXT NULL
- `created_at`: DATETIME NOT NULL

**Regras de Transição (`OS`)**:
- Ao mover para `ENTREGUE`, exige `motorista_saida_id` (ou nome informado) e preenche `data_entrega`, disparando opcionalmente a criação de um `Lembrete` preventivo.

---

### 8. `interacoes`
- `id`: INTEGER PK
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `usuario_id`: INTEGER FK -> `usuarios.id` NOT NULL
- `tipo`: ENUM(`LIGACAO`, `WHATSAPP`, `EMAIL`, `PRESENCIAL`, `SISTEMA`) NOT NULL
- `resumo`: TEXT NOT NULL
- `created_at`: DATETIME NOT NULL

---

### 9. `lembretes`
- `id`: INTEGER PK
- `cliente_id`: INTEGER FK -> `clientes.id` NOT NULL
- `veiculo_id`: INTEGER FK -> `veiculos.id` NULL
- `os_origem_id`: INTEGER FK -> `ordens_servico.id` NULL
- `usuario_responsavel_id`: INTEGER FK -> `usuarios.id` NOT NULL
- `tipo`: ENUM(`FOLLOW_UP`, `PREVENTIVA`) NOT NULL
- `titulo`: VARCHAR(160) NOT NULL
- `data_prevista`: DATE NOT NULL
- `km_previsto`: INTEGER NULL
- `status`: ENUM(`PENDENTE`, `CONCLUIDO`, `REAGENDADO`) NOT NULL DEFAULT `PENDENTE`
- `observacoes`: TEXT NULL
- `created_at`: DATETIME NOT NULL
