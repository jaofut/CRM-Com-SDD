# Feature Specification: CRM para Oficina de Veículos de Grande Porte

**Feature Branch**: `001-crm-oficina-pesados`

**Created**: 2026-11-24

**Status**: Draft

**Input**: CRM para oficina de veículos de grande porte focado em frotas/transportadoras B2B, com funil visual de orçamentos, conversão em Ordem de Serviço (OS) com checklist simplificado de entrada/saída, histórico de interações e lembretes de manutenção preventiva.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cadastro de Frotas, Contatos, Motoristas e Veículos (Priority: P1)

Como **Atendente/Consultor**, quero cadastrar empresas/transportadoras (clientes B2B) com seus respectivos contatos comerciais/gestores de frota, motoristas autorizados e veículos pesados (caminhões, carretas, ônibus), para centralizar todo o histórico da frota em um único lugar.

**Why this priority**: É a base de dados estrutural de todo o CRM. Sem o relacionamento entre Empresa → Veículos → Contatos/Motoristas, não é possível criar orçamentos, abrir OS ou registrar atendimentos.

**Independent Test**: Pode ser testado de forma independente criando uma transportadora com CNPJ, vinculando 2 contatos (ex.: Gestor de Frota e Financeiro), 1 motorista e 3 veículos por placa/chassi, e validando a busca rápida por CNPJ, nome fantasia ou placa.

**Acceptance Scenarios**:

1. **Given** que o atendente está na tela de clientes, **When** ele cadastra uma transportadora com Razão Social, Nome Fantasia, CNPJ e condições comerciais, **Then** o sistema salva a empresa e permite adicionar múltiplos contatos, motoristas e veículos vinculados a ela.
2. **Given** uma frota já cadastrada, **When** o atendente busca pela placa de um veículo ou pelo CNPJ da transportadora, **Then** o sistema exibe a ficha completa do cliente com a lista de veículos, contatos, motoristas e histórico resumido.
3. **Given** um veículo sendo cadastrado, **When** o atendente informa placa, marca/modelo, ano, tipo (cavalo mecânico, carreta, truck, ônibus, etc.), chassi e KM atual, **Then** o veículo fica vinculado à transportadora e disponível para seleção em orçamentos e OS.

---

### User Story 2 - Funil Visual de Orçamentos e Geração de PDF (Priority: P1)

Como **Atendente/Consultor**, quero gerenciar orçamentos em um funil visual (Kanban/etapas), gerar um PDF profissional para enviar ao gestor da frota (com atalho para WhatsApp Web) e converter orçamentos aprovados diretamente em Ordem de Serviço (OS).

**Why this priority**: É o coração comercial do CRM para oficinas B2B, onde negociações com frotistas acontecem e onde se garante que nenhum orçamento enviado fique perdido sem acompanhamento.

**Independent Test**: Pode ser testado criando um orçamento para um veículo da frota com itens de peças e mão de obra, movendo-o entre as etapas do funil, exportando o PDF e clicando em "Converter em OS" após aprovação.

**Acceptance Scenarios**:

1. **Given** um cliente e veículo selecionados, **When** o atendente cria um orçamento adicionando peças, serviços (mão de obra), descontos e validade, **Then** o orçamento entra na etapa `Rascunho` do funil com o valor total calculado automaticamente.
2. **Given** um orçamento criado, **When** o atendente gera o PDF e aciona o atalho de WhatsApp Web para o contato do gestor da frota, **Then** o sistema gera o documento formatado com dados da oficina, cliente, veículo e itens, e abre o WhatsApp Web com mensagem pré-preenchida, permitindo mover o card para `Enviado` ou `Em Negociação`.
3. **Given** um orçamento na etapa `Enviado` ou `Em Negociação`, **When** o atendente registra a aprovação (podendo informar nº de Pedido de Compra/PO ou observação do gestor) e aciona a conversão, **Then** o orçamento passa para `Aprovado` e uma nova OS é criada automaticamente herdando cliente, veículo, contato e itens aprovados.
4. **Given** um orçamento recusado pelo cliente, **When** o atendente move para `Recusado`, **Then** o sistema solicita o motivo da recusa (ex.: preço, prazo, concorrência) para histórico gerencial.

---

### User Story 3 - Ordem de Serviço (OS) com Checklist de Entrada/Saída e Acompanhamento (Priority: P1)

Como **Atendente/Consultor**, quero registrar a entrada e a saída do veículo na OS com um checklist simplificado (KM, motorista que entregou/retirou e avarias pré-existentes) e atualizar o status da execução até a entrega, para manter controle operacional e transparência com a transportadora.

**Why this priority**: Completa o ciclo operacional prometido pelo MVP, evitando divergências sobre estado do veículo na entrega e dando visibilidade em tempo real de quais veículos estão no pátio e em qual estágio.

**Independent Test**: Pode ser testado abrindo uma OS (diretamente ou a partir de um orçamento aprovado), preenchendo o checklist de entrada, avançando o status até `Pronta` e concluindo o checklist de saída para `Entregue`.

**Acceptance Scenarios**:

1. **Given** uma OS recém-aberta, **When** o veículo chega à oficina e o atendente preenche o checklist de entrada (KM atual, motorista que entregou, observações de avarias/itens deixados no veículo), **Then** o sistema registra data/hora da entrada e atualiza a última quilometragem conhecida do veículo.
2. **Given** uma OS em andamento, **When** o atendente atualiza o status conforme o retorno da oficina (`Aguardando Peça`, `Em Execução`, `Em Teste`, `Pronta`), **Then** o painel de OS em aberto reflete o status atual e registra o histórico de mudanças com usuário e timestamp.
3. **Given** uma OS com status `Pronta`, **When** o motorista da transportadora retira o veículo e o atendente preenche os dados de saída (motorista que retirou, observações finais), **Then** a OS passa para `Entregue`, libera a geração de PDF da OS finalizada e atualiza a data de referência para revisões futuras.

---

### User Story 4 - Timeline de Interações e Lembretes de Manutenção Preventiva (Priority: P2)

Como **Atendente/Consultor**, quero registrar todas as interações com a transportadora (ligações, mensagens, visitas) em uma timeline e receber lembretes de manutenção preventiva (por data ou estimativa de KM) para realizar pós-venda e gerar recorrência.

**Why this priority**: Diferencia o sistema de um simples emissor de OS, transformando-o em um CRM ativo que retém frotas e gera receita previsível por meio de revisões programadas.

**Independent Test**: Pode ser testado registrando uma interação manual na ficha de uma transportadora, configurando um lembrete preventivo de 90 dias ou +10.000 km após uma OS entregue e verificando a listagem de lembretes pendentes no painel do atendente.

**Acceptance Scenarios**:

1. **Given** a ficha de uma transportadora, **When** o atendente registra uma interação (tipo: Ligação, WhatsApp, E-mail ou Presencial, resumo e próxima ação opcional), **Then** a entrada aparece em ordem cronológica na timeline do cliente junto com eventos automáticos de orçamentos e OS.
2. **Given** uma OS concluída/entregue para um veículo, **When** o atendente define ou o sistema aplica uma regra de retorno preventivo (por intervalo de dias, ex.: 90/180 dias, ou estimativa de KM), **Then** um lembrete é agendado automaticamente para a data prevista.
3. **Given** lembretes vencidos ou próximos do vencimento, **When** o atendente acessa a tela de "Follow-ups e Preventivas do Dia", **Then** ele visualiza a lista priorizada com contato do gestor, placa do veículo, última OS e botão de atalho para WhatsApp Web, podendo marcar o lembrete como concluído ou reagendado.

---

### User Story 5 - Controle de Acesso (2 Perfis) e Painel Gerencial (Priority: P2)

Como **Administrador/Gerente**, quero gerenciar usuários nos perfis `Administrador/Gerente` e `Atendente/Consultor` e visualizar indicadores consolidados de conversão de orçamentos, OS em andamento e motivos de recusa, para acompanhar a saúde comercial e operacional da oficina.

**Why this priority**: Garante governança de acesso e dá ao gestor da oficina a visibilidade necessária para tomar decisões comerciais sem depender de planilhas paralelas.

**Independent Test**: Pode ser testado autenticando com um usuário `Administrador/Gerente` (acesso a gestão de usuários e dashboard gerencial completo) e com um usuário `Atendente/Consultor` (acesso restrito à operação diária, sem gestão de usuários/relatórios gerenciais sensíveis).

**Acceptance Scenarios**:

1. **Given** um usuário não autenticado, **When** acessa o sistema, **Then** deve realizar login com e-mail e senha para acessar as funcionalidades correspondentes ao seu perfil.
2. **Given** um usuário autenticado como `Administrador/Gerente`, **When** acessa o painel gerencial, **Then** visualiza métricas do período (total orçado vs. aprovado, taxa de conversão, OS por status, faturamento estimado de OS entregues e principais motivos de recusa de orçamento) e pode criar/desativar contas de usuários.
3. **Given** um usuário autenticado como `Atendente/Consultor`, **When** tenta acessar configurações de usuários ou relatórios gerenciais restritos, **Then** o sistema bloqueia o acesso e exibe apenas sua área operacional (clientes, funil, OS e follow-ups).

---

### Edge Cases

- **CNPJ duplicado**: O sistema deve impedir o cadastro de duas empresas com o mesmo CNPJ ativo, alertando o usuário e oferecendo link para abrir o cadastro existente.
- **Placa duplicada ou transferência de veículo entre frotas**: Se uma placa já estiver cadastrada em outra transportadora, o sistema deve alertar o atendente e permitir transferir/vincular o veículo à nova frota preservando ou separando claramente o histórico anterior, em vez de criar registros duplicados.
- **KM regressiva na entrada da OS**: Caso o atendente informe uma KM menor que a última registrada para o veículo, o sistema deve exibir um alerta de validação (ex.: troca de painel/erro de digitação) exigindo confirmação antes de salvar.
- **Orçamento aprovado com alteração posterior**: Após um orçamento ser convertido em OS, alterações de escopo devem exigir registro na OS (aditivo/novo orçamento vinculado) sem apagar o histórico do orçamento originalmente aprovado.
- **Desativação de usuário com histórico**: Um usuário desativado pelo Administrador não pode mais fazer login, mas seu nome deve permanecer visível no histórico de orçamentos, OS e interações passadas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST autenticar usuários por e-mail e senha (armazenada com hash seguro) e aplicar controle de acesso no servidor baseado em 2 perfis: `Administrador/Gerente` e `Atendente/Consultor`.
- **FR-002**: O sistema MUST permitir o cadastro e edição de Clientes B2B (Transportadoras/Frotas) com Razão Social, Nome Fantasia, CNPJ único, endereço, observações comerciais e status (Ativo/Inativo).
- **FR-003**: O sistema MUST permitir vincular múltiplos Contatos (nome, cargo/função, telefone/WhatsApp, e-mail) e múltiplos Motoristas (nome, CPF/CNH opcional, telefone) a cada Cliente B2B.
- **FR-004**: O sistema MUST permitir o cadastro de múltiplos Veículos por Cliente, contendo placa, marca/modelo, ano, tipo de veículo pesado, chassi (opcional) e quilometragem (KM) atualizada.
- **FR-005**: O sistema MUST disponibilizar busca global rápida por Razão Social, Nome Fantasia, CNPJ ou Placa do veículo.
- **FR-006**: O sistema MUST oferecer um funil visual (Kanban/etapas) de Orçamentos com os estados: `Rascunho`, `Enviado`, `Em Negociação`, `Aprovado` e `Recusado`.
- **FR-007**: O sistema MUST permitir compor orçamentos com itens de peças e serviços (descrição, quantidade, valor unitário, desconto), calculando subtotais e total geral automaticamente.
- **FR-008**: O sistema MUST gerar arquivo PDF formatado para Orçamentos e para Ordens de Serviço finalizadas, e disponibilizar atalho para abrir conversa no WhatsApp Web com o contato selecionado.
- **FR-009**: O sistema MUST permitir converter um Orçamento `Aprovado` em uma Ordem de Serviço (OS) em um clique, copiando cliente, veículo, contato e itens, além de permitir abertura direta de OS quando aplicável.
- **FR-010**: A Ordem de Serviço MUST suportar checklist simplificado de entrada (KM de entrada, motorista que entregou, observações de avarias) e de saída (motorista que retirou, observações finais), além dos status operacionais: `Aguardando Peça`, `Em Execução`, `Em Teste`, `Pronta` e `Entregue`.
- **FR-011**: O sistema MUST manter uma timeline de interações por Cliente combinando registros manuais (ligação, WhatsApp, e-mail, visita) e eventos automáticos do ciclo de orçamento e OS.
- **FR-012**: O sistema MUST permitir criar lembretes manuais de follow-up e gerar lembretes automáticos de manutenção preventiva baseados em intervalo de dias definido na entrega (padrão sugerido de 90 dias, ajustável pelo atendente) com registro opcional do KM previsto para a próxima revisão, exibindo uma fila diária de pendências para o atendente.
- **FR-013**: O sistema MUST fornecer ao perfil `Administrador/Gerente` um painel gerencial com total orçado vs. aprovado, taxa de conversão, quantidade de OS por status e motivos de recusa de orçamentos.
- **FR-014**: O sistema MUST preservar integralmente registros históricos (orçamentos, OS, interações e autoria de usuários desativados), utilizando inativação lógica em vez de exclusão física.

### Key Entities

- **Usuário**: Pessoa interna da oficina que acessa o sistema (`nome`, `email`, `senha_hash`, `perfil` [Admin | Atendente], `ativo`).
- **Cliente (Frota/Transportadora)**: Empresa contratante (`razao_social`, `nome_fantasia`, `cnpj`, `endereco`, `condicoes_comerciais`, `ativo`).
- **Contato**: Pessoa de relacionamento da empresa (`cliente_id`, `nome`, `cargo`, `telefone_whatsapp`, `email`, `principal`).
- **Motorista**: Condutor vinculado à frota responsável por entregar/retirar veículos (`cliente_id`, `nome`, `telefone`, `documento_opcional`).
- **Veículo**: Ativo da frota atendido pela oficina (`cliente_id`, `placa`, `tipo`, `marca_modelo`, `ano`, `chassi`, `km_atual`).
- **Orçamento**: Proposta comercial vinculada a um Cliente, Contato e Veículo (`numero`, `etapa_funil`, `validade`, `itens`, `desconto`, `valor_total`, `motivo_recusa`, `po_aprovacao`).
- **Ordem de Serviço (OS)**: Registro de execução do serviço (`numero`, `orcamento_id_opcional`, `cliente_id`, `veiculo_id`, `status_os`, `km_entrada`, `motorista_entrada_id`, `avarias_entrada`, `motorista_saida_id`, `observacoes_saida`, `data_entrada`, `data_entrega`).
- **Interação**: Registro na timeline do cliente (`cliente_id`, `usuario_id`, `tipo`, `descricao`, `data_hora`).
- **Lembrete / Preventiva**: Tarefa de contato futuro (`cliente_id`, `veiculo_id_opcional`, `os_origem_id_opcional`, `tipo` [Follow-up | Preventiva], `data_prevista`, `km_previsto_opcional`, `status` [Pendente | Concluido | Reagendado]).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um atendente consegue cadastrar uma nova transportadora com 1 contato e 1 veículo e gerar o primeiro orçamento em PDF em menos de 4 minutos.
- **SC-002**: 100% dos orçamentos aprovados podem ser convertidos em Ordem de Serviço sem redigitação de dados do cliente, veículo ou itens.
- **SC-003**: A busca por placa de veículo ou CNPJ retorna a ficha completa da frota e seu histórico em menos de 2 segundos.
- **SC-004**: O gestor da oficina consegue visualizar em uma única tela a taxa de conversão de orçamentos e a distribuição atual de todas as OS abertas no pátio.
- **SC-005**: 100% das OS concluídas possuem registro de quem entregou e quem retirou o veículo e atualizam a KM do veículo no histórico da frota.

## Assumptions

- **Público e operação**: A oficina atende predominantemente frotas/transportadoras B2B (caminhões, carretas e ônibus), e os mecânicos não operam o sistema diretamente — o lançamento e a atualização de status são feitos pelos atendentes/consultores.
- **Escopo de integrações na v1**: Não haverá integração com API oficial do WhatsApp (disparos automáticos), consulta automática de CNPJ/placa em APIs externas nem emissão fiscal (NF-e/NFS-e) nesta primeira versão; o contato via WhatsApp será feito por atalho para WhatsApp Web e o envio formal por PDF.
- **Limites de escopo (fora da v1)**: Controle detalhado de estoque de peças, ordens de compra, alocação de boxes/mecânicos e módulo financeiro completo (contas a pagar/receber, boletos) ficam fora desta especificação inicial.
- **Conectividade**: Os usuários utilizarão o sistema em computadores/tablets na recepção e escritório da oficina com conexão estável à internet.
