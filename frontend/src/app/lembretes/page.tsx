"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, CalendarClock } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface Lembrete {
  id: number;
  tipo: string;
  titulo: string;
  data_prevista: string;
  km_previsto: number | null;
  status: string;
  cliente_nome: string | null;
  veiculo_placa: string | null;
}

export default function LembretesPage() {
  const [lembretes, setLembretes] = useState<Lembrete[]>([]);

  async function load() {
    const data = await apiFetch<Lembrete[]>("/lembretes?status=PENDENTE");
    setLembretes(data);
  }

  useEffect(() => {
    load();
  }, []);

  async function concluir(id: number) {
    await apiFetch(`/lembretes/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "CONCLUIDO" }),
    });
    await load();
  }

  async function reagendar(id: number) {
    const novaData = window.prompt("Nova data (AAAA-MM-DD):");
    if (!novaData) return;
    await apiFetch(`/lembretes/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "REAGENDADO", data_prevista: novaData }),
    });
    await load();
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Follow-ups e Preventivas</h1>
        <p className="text-sm text-slate-500">Fila de retornos programados e revisões preventivas</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
        {lembretes.map((l) => (
          <div key={l.id} className="p-4 flex items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                  {l.tipo}
                </span>
                <span className="font-semibold text-slate-900">{l.titulo}</span>
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {l.cliente_nome} {l.veiculo_placa ? `• Placa ${l.veiculo_placa}` : ""} • Previsto para{" "}
                <span className="font-medium text-slate-700">{l.data_prevista}</span>
                {l.km_previsto ? ` (${l.km_previsto.toLocaleString("pt-BR")} km)` : ""}
              </div>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => reagendar(l.id)}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium hover:bg-slate-50"
              >
                <CalendarClock className="w-3.5 h-3.5" /> Reagendar
              </button>
              <button
                type="button"
                onClick={() => concluir(l.id)}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-medium hover:bg-emerald-700"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Concluir
              </button>
            </div>
          </div>
        ))}
        {lembretes.length === 0 && (
          <div className="p-8 text-center text-sm text-slate-400">
            Nenhum lembrete pendente no momento.
          </div>
        )}
      </div>
    </AppShell>
  );
}
