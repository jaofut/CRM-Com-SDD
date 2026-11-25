"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { FileDown } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch, downloadPdf } from "@/lib/api";

interface Motorista {
  id: number;
  nome: string;
}

interface OSDetalhe {
  id: number;
  numero: string;
  cliente_id: number;
  cliente_nome: string | null;
  veiculo_placa: string | null;
  status: string;
  km_entrada: number;
  avarias_entrada: string | null;
  motorista_entrada_nome: string | null;
  motorista_saida_nome: string | null;
  observacoes_saida: string | null;
  valor_total: string;
  itens: { id: number; tipo: string; descricao: string; quantidade: string; valor_unitario: string; subtotal: string }[];
  historico: { id: number; status_anterior: string | null; status_novo: string; observacao: string | null; created_at: string }[];
}

export default function OsDetalhePage() {
  const params = useParams<{ id: string }>();
  const osId = params.id;
  const [os, setOs] = useState<OSDetalhe | null>(null);
  const [motoristas, setMotoristas] = useState<Motorista[]>([]);
  const [novoStatus, setNovoStatus] = useState("");
  const [motSaidaId, setMotSaidaId] = useState("");
  const [obsSaida, setObsSaida] = useState("");
  const [preventivaDias, setPreventivaDias] = useState("90");
  const [erro, setErro] = useState<string | null>(null);

  const load = useCallback(async () => {
    const data = await apiFetch<OSDetalhe>(`/ordens-servico/${osId}`);
    setOs(data);
    setNovoStatus(data.status);
    const cli = await apiFetch<{ motoristas: Motorista[] }>(`/clientes/${data.cliente_id}`);
    setMotoristas(cli.motoristas);
    if (cli.motoristas[0]) setMotSaidaId(String(cli.motoristas[0].id));
  }, [osId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleAtualizarStatus(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch(`/ordens-servico/${osId}/status`, {
        method: "PATCH",
        body: JSON.stringify({
          status: novoStatus,
          motorista_saida_id: novoStatus === "ENTREGUE" && motSaidaId ? Number(motSaidaId) : undefined,
          observacoes_saida: novoStatus === "ENTREGUE" ? obsSaida || null : undefined,
          preventiva_dias: novoStatus === "ENTREGUE" ? Number(preventivaDias) || 90 : undefined,
        }),
      });
      await load();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao atualizar status");
    }
  }

  if (!os) {
    return (
      <AppShell>
        <div className="text-sm text-slate-500">Carregando OS...</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{os.numero}</h1>
          <p className="text-sm text-slate-500">
            {os.cliente_nome} • Placa <span className="font-mono font-semibold">{os.veiculo_placa}</span> • KM Entrada: {os.km_entrada.toLocaleString("pt-BR")}
          </p>
        </div>
        <button
          type="button"
          onClick={() => downloadPdf(`/ordens-servico/${os.id}/pdf`, `${os.numero}.pdf`)}
          className="inline-flex items-center gap-2 rounded-lg bg-slate-900 text-white px-4 py-2 text-sm font-medium"
        >
          <FileDown className="w-4 h-4" /> Baixar PDF
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h2 className="font-bold text-slate-900 mb-3">Checklist Entrada / Saída</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-slate-500 text-xs">Motorista Entrada</div>
                <div className="font-medium">{os.motorista_entrada_nome || "Não informado"}</div>
              </div>
              <div>
                <div className="text-slate-500 text-xs">Motorista Saída</div>
                <div className="font-medium">{os.motorista_saida_nome || "Pendente"}</div>
              </div>
              <div className="col-span-2">
                <div className="text-slate-500 text-xs">Avarias / Observações Entrada</div>
                <div>{os.avarias_entrada || "Sem observações"}</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-5 py-3 border-b border-slate-200 font-bold text-slate-900">
              Itens da OS — Total: R$ {Number(os.valor_total).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-2">Tipo</th>
                  <th className="px-4 py-2">Descrição</th>
                  <th className="px-4 py-2">Qtd</th>
                  <th className="px-4 py-2 text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {os.itens.map((i) => (
                  <tr key={i.id}>
                    <td className="px-4 py-2 text-xs">{i.tipo}</td>
                    <td className="px-4 py-2">{i.descricao}</td>
                    <td className="px-4 py-2">{i.quantidade}</td>
                    <td className="px-4 py-2 text-right font-medium">R$ {Number(i.subtotal).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-6">
          <form onSubmit={handleAtualizarStatus} className="bg-white rounded-xl border border-slate-200 p-5 space-y-3">
            <h2 className="font-bold text-slate-900">Atualizar Status</h2>
            <select
              value={novoStatus}
              onChange={(e) => setNovoStatus(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="AGUARDANDO_PECA">Aguardando Peça</option>
              <option value="EM_EXECUCAO">Em Execução</option>
              <option value="EM_TESTE">Em Teste</option>
              <option value="PRONTA">Pronta</option>
              <option value="ENTREGUE">Entregue</option>
            </select>

            {novoStatus === "ENTREGUE" && (
              <>
                <select
                  required
                  value={motSaidaId}
                  onChange={(e) => setMotSaidaId(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">Motorista que retirou</option>
                  {motoristas.map((m) => (
                    <option key={m.id} value={m.id}>{m.nome}</option>
                  ))}
                </select>
                <input
                  placeholder="Observações da entrega"
                  value={obsSaida}
                  onChange={(e) => setObsSaida(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Preventiva (dias)</label>
                  <input
                    type="number"
                    min={1}
                    value={preventivaDias}
                    onChange={(e) => setPreventivaDias(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>
              </>
            )}

            {erro && <p className="text-xs text-red-600">{erro}</p>}
            <button type="submit" className="w-full rounded-lg bg-amber-500 text-slate-950 font-semibold py-2 text-sm">
              Salvar Status
            </button>
          </form>

          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h2 className="font-bold text-slate-900 mb-3">Histórico de Status</h2>
            <div className="space-y-2 text-xs">
              {os.historico.map((h) => (
                <div key={h.id} className="border-l-2 border-amber-500 pl-2.5 py-0.5">
                  <div className="font-semibold text-slate-800">{h.status_novo}</div>
                  {h.observacao && <div className="text-slate-600">{h.observacao}</div>}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
