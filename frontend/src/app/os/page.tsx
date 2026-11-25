"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ClipboardList } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface OSResumo {
  id: number;
  numero: string;
  status: string;
  cliente_nome: string | null;
  veiculo_placa: string | null;
  km_entrada: number;
  valor_total: string;
  data_entrada: string;
}

const STATUS_LABELS: Record<string, string> = {
  AGUARDANDO_PECA: "Aguardando Peça",
  EM_EXECUCAO: "Em Execução",
  EM_TESTE: "Em Teste",
  PRONTA: "Pronta",
  ENTREGUE: "Entregue",
};

export default function OrdensServicoPage() {
  const [ordens, setOrdens] = useState<OSResumo[]>([]);
  const [statusFilter, setStatusFilter] = useState("");

  async function load(st = "") {
    const q = st ? `?status=${encodeURIComponent(st)}` : "";
    const data = await apiFetch<OSResumo[]>(`/ordens-servico${q}`);
    setOrdens(data);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Ordens de Serviço (OS)</h1>
          <p className="text-sm text-slate-500">Acompanhamento de pátio, checklist e entregas</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            load(e.target.value);
          }}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
        >
          <option value="">Todos os status</option>
          {Object.entries(STATUS_LABELS).map(([k, label]) => (
            <option key={k} value={k}>{label}</option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">Número</th>
              <th className="px-4 py-3 font-medium">Frota</th>
              <th className="px-4 py-3 font-medium">Placa</th>
              <th className="px-4 py-3 font-medium">KM Entrada</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Total</th>
              <th className="px-4 py-3 font-medium text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {ordens.map((o) => (
              <tr key={o.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-mono font-semibold text-slate-900 flex items-center gap-2">
                  <ClipboardList className="w-4 h-4 text-amber-600" />
                  {o.numero}
                </td>
                <td className="px-4 py-3">{o.cliente_nome}</td>
                <td className="px-4 py-3 font-mono">{o.veiculo_placa}</td>
                <td className="px-4 py-3">{o.km_entrada.toLocaleString("pt-BR")} km</td>
                <td className="px-4 py-3">
                  <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                    {STATUS_LABELS[o.status] || o.status}
                  </span>
                </td>
                <td className="px-4 py-3 font-medium">
                  R$ {Number(o.valor_total).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </td>
                <td className="px-4 py-3 text-right">
                  <Link href={`/os/${o.id}`} className="text-amber-600 hover:text-amber-700 font-medium">
                    Gerenciar OS →
                  </Link>
                </td>
              </tr>
            ))}
            {ordens.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                  Nenhuma OS encontrada.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
