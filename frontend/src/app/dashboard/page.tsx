"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface DashboardData {
  total_orcamentos: number;
  total_orcado: string;
  total_aprovado: string;
  taxa_conversao_percent: number;
  os_por_status: Record<string, number>;
  valor_os_entregues: string;
  motivos_recusa: { motivo: string; quantidade: number }[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<DashboardData>("/dashboard/gerencial")
      .then(setData)
      .catch((err) => setErro(err instanceof Error ? err.message : "Acesso restrito"));
  }, []);

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Painel Gerencial</h1>
        <p className="text-sm text-slate-500">Indicadores de conversão, pátio de OS e motivos de recusa</p>
      </div>

      {erro && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">{erro}</div>
      )}

      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500">Total Orçado</div>
              <div className="text-xl font-bold text-slate-900 mt-1">
                R$ {Number(data.total_orcado).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-slate-400 mt-1">{data.total_orcamentos} orçamentos</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500">Total Aprovado</div>
              <div className="text-xl font-bold text-emerald-700 mt-1">
                R$ {Number(data.total_aprovado).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500">Taxa de Conversão</div>
              <div className="text-xl font-bold text-amber-600 mt-1">{data.taxa_conversao_percent}%</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500">Faturamento OS Entregues</div>
              <div className="text-xl font-bold text-slate-900 mt-1">
                R$ {Number(data.valor_os_entregues).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="font-bold text-slate-900 mb-3">OS por Status</h2>
              <div className="space-y-2 text-sm">
                {Object.entries(data.os_por_status).map(([st, qtd]) => (
                  <div key={st} className="flex items-center justify-between py-1 border-b border-slate-100 last:border-0">
                    <span className="text-slate-600">{st}</span>
                    <span className="font-bold text-slate-900">{qtd}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="font-bold text-slate-900 mb-3">Motivos de Recusa</h2>
              <div className="space-y-2 text-sm">
                {data.motivos_recusa.map((m) => (
                  <div key={m.motivo} className="flex items-center justify-between py-1 border-b border-slate-100 last:border-0">
                    <span className="text-slate-600">{m.motivo}</span>
                    <span className="font-bold text-red-600">{m.quantidade}</span>
                  </div>
                ))}
                {data.motivos_recusa.length === 0 && (
                  <p className="text-slate-400">Nenhuma recusa registrada.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
