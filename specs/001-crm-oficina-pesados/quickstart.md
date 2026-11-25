# Quickstart & Validation Guide: CRM Oficina de Veículos de Grande Porte

**Feature**: `001-crm-oficina-pesados`

## Pré-requisitos
- **Python 3.11+** (com `pip` / `venv`)
- **Node.js 20+** (com `npm`)
- Nenhuma instância externa de banco de dados é necessária (SQLite local).

## 1. Subindo o Backend (FastAPI + SQLite)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed   # Cria usuário ADMIN e ATENDENTE iniciais
uvicorn app.main:app --reload --port 8000
```

- Documentação interativa da API: `http://localhost:8000/docs`
- Arquivo SQLite criado em: `backend/data/crm.db`

## 2. Subindo o Frontend (Next.js)

```powershell
cd frontend
npm install
npm run dev
```

- Aplicação web disponível em: `http://localhost:3000`

## 3. Executando Testes

```powershell
# Backend (pytest + httpx)
cd backend
pytest

# Frontend (Vitest / TypeScript check)
cd frontend
npm run typecheck
npm test
```

## 4. Cenários de Validação Ponta a Ponta (MVP)

1. **Login e RBAC (US5)**:
   - Acessar `/login` como `ATENDENTE` e confirmar acesso ao funil, clientes e OS, mas bloqueio ao painel gerencial/gestão de usuários (`403` na API e menu oculto na UI).
   - Acessar como `ADMIN` e confirmar visualização do painel gerencial (`/dashboard`) e criação de novo usuário.
2. **Cadastro de Frota e Busca Global (US1)**:
   - Cadastrar transportadora com CNPJ único, 2 contatos, 1 motorista e 2 veículos pesados.
   - Tentar cadastrar outro cliente com mesmo CNPJ e validar bloqueio (`409`).
   - Buscar pela placa na barra global e confirmar retorno da ficha completa em `< 2s`.
3. **Funil de Orçamentos, PDF e Conversão em OS (US2)**:
   - Criar orçamento com peças e serviços → verificar etapa `Rascunho`.
   - Gerar PDF (`/api/v1/orcamentos/{id}/pdf`) e testar atalho de WhatsApp Web.
   - Mover para `Enviado` → `Aprovado` e acionar **Converter em OS** verificando cópia integral de cliente, veículo e itens.
4. **Checklist e Ciclo da OS (US3)**:
   - Registrar entrada com KM, motorista e avarias. Testar alerta de KM menor que `km_atual`.
   - Avançar status até `Pronta` e concluir entrega (`Entregue`) registrando motorista de saída e gerando PDF da OS.
5. **Timeline e Preventivas (US4)**:
   - Registrar interação manual na ficha da transportadora e validar ordem cronológica na timeline.
   - Verificar lembrete preventivo gerado na entrega da OS listado na fila de pendências do dia.
