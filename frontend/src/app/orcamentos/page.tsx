"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { OrcamentoKanban, type OrcamentoCard } from "@/components/OrcamentoKanban";
import { apiFetch } from "@/lib/api";

interface ClienteResumo {
  id: number;
  nome_fantasia: string;
}

interface ClienteDetalhe {
  id: number;
  contatos: { id: number; nome: string }[];
  veiculos: { id: number; placa: string; marca_modelo: string; km_atual: number }[];
}

export default function OrcamentosPage() {
  const router = useRouter();
  const [orcamentos, setOrcamentos] = useState<OrcamentoCard[]>([]);
  const [clientes, setClientes] = useState<ClienteResumo[]>([]);
  const [showModal, setShowModal] = useState(false);

  const [clienteId, setClienteId] = useState<string>("");
  const [detalhe, setDetalhe] = useState<ClienteDetalhe | null>(null);
  const [contatoId, setContatoId] = useState<string>("");
  const [veiculoId, setVeiculoId] = useState<string>("");
  const [desconto, setDesconto] = useState("0");
  const [itens, setItens] = useState([
    { tipo: "SERVICO", descricao: "", quantidade: "1", valor_unitario: "0" },
  ]);
  const [erro, setErro] = useState<string | null>(null);

  const load = useCallback(async () => {
    const [orcs, clis] = await Promise.all([
      apiFetch<OrcamentoCard[]>("/orcamentos"),
      apiFetch<ClienteResumo[]>("/clientes?ativo=true"),
    ]);
    setOrcamentos(orcs);
    setClientes(clis);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSelectCliente(id: string) {
    setClienteId(id);
    setContatoId("");
    setVeiculoId("");
    if (!id) {
      setDetalhe(null);
      return;
    }
    const d = await apiFetch<ClienteDetalhe>(`/clientes/${id}`);
    setDetalhe(d);
    if (d.contatos[0]) setContatoId(String(d.contatos[0].id));
    if (d.veiculos[0]) setVeiculoId(String(d.veiculos[0].id));
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch("/orcamentos", {
        method: "POST",
        body: JSON.stringify({
          cliente_id: Number(clienteId),
          contato_id: Number(contatoId),
          veiculo_id: Number(veiculoId),
          desconto_total: Number(desconto) || 0,
          itens: itens.map((i) => ({
            tipo: i.tipo,
            descricao: i.descricao,
            quantidade: Number(i.quantidade),
            valor_unitario: Number(i.valor_unitario),
          })),
        }),
      });
      setShowModal(false);
      await load();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao criar orçamento");
    }
  }

  async function handleMoverEtapa(orc: OrcamentoCard, novaEtapa: OrcamentoCard["etapa"]) {
    let motivo_recusa: string | undefined;
    let po_aprovacao: string | undefined;

    if (novaEtapa === "RECUSADO") {
      const m = window.prompt("Informe o motivo da recusa:");
      if (!m || !m.trim()) return;
      motivo_recusa = m.trim();
    } else if (novaEtapa === "APROVADO") {
      const po = window.prompt("Número do Pedido de Compra / PO (opcional):") || "";
      po_aprovacao = po.trim() || undefined;
    }

    await apiFetch(`/orcamentos/${orc.id}/etapa`, {
      method: "PATCH",
      body: JSON.stringify({ etapa: novaEtapa, motivo_recusa, po_aprovacao }),
    });
    await load();
  }

  async function handleConverterOs(orc: OrcamentoCard) {
    const kmStr = window.prompt("KM de entrada do veículo na oficina:");
    if (kmStr === null) return;
    const km = Number(kmStr);
    if (Number.isNaN(km) || km < 0) return;

    try {
      const os = await apiFetch<{ id: number }>(`/orcamentos/${orc.id}/converter-os`, {
        method: "POST",
        body: JSON.stringify({ km_entrada: km, confirmar_km_menor: false }),
      });
      router.push(`/os/${os.id}`);
    } catch (err) {
      if (
        err instanceof Error &&
        err.message.toLowerCase().includes("menor") &&
        window.confirm(`${err.message}. Confirmar KM mesmo assim?`)
      ) {
        const os = await apiFetch<{ id: number }>(`/orcamentos/${orc.id}/converter-os`, {
          method: "POST",
          body: JSON.stringify({ km_entrada: km, confirmar_km_menor: true }),
        });
        router.push(`/os/${os.id}`);
      } else {
        alert(err instanceof Error ? err.message : "Erro ao converter OS");
      }
    }
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Funil de Orçamentos</h1>
          <p className="text-sm text-slate-500">Kanban comercial, PDF, WhatsApp Web e conversão em OS</p>
        </div>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-slate-900 text-white px-4 py-2 text-sm font-medium hover:bg-slate-800"
        >
          <Plus className="w-4 h-4" />
          Novo Orçamento
        </button>
      </div>

      <OrcamentoKanban
        orcamentos={orcamentos}
        onMoverEtapa={handleMoverEtapa}
        onConverterOs={handleConverterOs}
      />

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-xl max-h-[90vh] overflow-auto">
            <h2 className="text-lg font-bold mb-4">Novo Orçamento</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <select
                  required
                  value={clienteId}
                  onChange={(e) => handleSelectCliente(e.target.value)}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">Selecione a Frota</option>
                  {clientes.map((c) => (
                    <option key={c.id} value={c.id}>{c.nome_fantasia}</option>
                  ))}
                </select>
                <select
                  required
                  value={contatoId}
                  onChange={(e) => setContatoId(e.target.value)}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">Contato</option>
                  {detalhe?.contatos.map((c) => (
                    <option key={c.id} value={c.id}>{c.nome}</option>
                  ))}
                </select>
                <select
                  required
                  value={veiculoId}
                  onChange={(e) => setVeiculoId(e.target.value)}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">Veículo</option>
                  {detalhe?.veiculos.map((v) => (
                    <option key={v.id} value={v.id}>{v.placa} - {v.marca_modelo}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-700">Itens (Peças e Serviços)</span>
                  <button
                    type="button"
                    onClick={() =>
                      setItens([...itens, { tipo: "PECA", descricao: "", quantidade: "1", valor_unitario: "0" }])
                    }
                    className="text-xs font-medium text-amber-600"
                  >
                    + Adicionar item
                  </button>
                </div>
                {itens.map((item, idx) => (
                  <div key={idx} className="grid grid-cols-12 gap-2">
                    <select
                      value={item.tipo}
                      onChange={(e) => {
                        const copy = [...itens];
                        copy[idx].tipo = e.target.value;
                        setItens(copy);
                      }}
                      className="col-span-2 rounded border border-slate-300 px-2 py-1.5 text-xs"
                    >
                      <option value="SERVICO">Serviço</option>
                      <option value="PECA">Peça</option>
                    </select>
                    <input
                      required
                      placeholder="Descrição"
                      value={item.descricao}
                      onChange={(e) => {
                        const copy = [...itens];
                        copy[idx].descricao = e.target.value;
                        setItens(copy);
                      }}
                      className="col-span-6 rounded border border-slate-300 px-2 py-1.5 text-xs"
                    />
                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      required
                      placeholder="Qtd"
                      value={item.quantidade}
                      onChange={(e) => {
                        const copy = [...itens];
                        copy[idx].quantidade = e.target.value;
                        setItens(copy);
                      }}
                      className="col-span-2 rounded border border-slate-300 px-2 py-1.5 text-xs"
                    />
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      required
                      placeholder="Unitário"
                      value={item.valor_unitario}
                      onChange={(e) => {
                        const copy = [...itens];
                        copy[idx].valor_unitario = e.target.value;
                        setItens(copy);
                      }}
                      className="col-span-2 rounded border border-slate-300 px-2 py-1.5 text-xs"
                    />
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-3">
                <label className="text-sm text-slate-600">Desconto (R$):</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={desconto}
                  onChange={(e) => setDesconto(e.target.value)}
                  className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-32"
                />
              </div>

              {erro && <p className="text-sm text-red-600">{erro}</p>}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm rounded-lg border border-slate-200"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm rounded-lg bg-slate-900 text-white font-medium"
                >
                  Criar Orçamento
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
