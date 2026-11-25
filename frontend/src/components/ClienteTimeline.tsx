"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface InteracaoItem {
  id: number;
  tipo: string;
  resumo: string;
  usuario_nome: string | null;
  created_at: string;
}

export function ClienteTimeline({ clienteId }: { clienteId: string }) {
  const [itens, setItens] = useState<InteracaoItem[]>([]);
  const [tipo, setTipo] = useState("LIGACAO");
  const [resumo, setResumo] = useState("");

  const load = useCallback(async () => {
    const data = await apiFetch<InteracaoItem[]>(`/clientes/${clienteId}/interacoes`);
    setItens(data);
  }, [clienteId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!resumo.trim()) return;
    await apiFetch(`/clientes/${clienteId}/interacoes`, {
      method: "POST",
      body: JSON.stringify({ tipo, resumo }),
    });
    setResumo("");
    await load();
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-4 flex flex-wrap gap-2">
        <select
          value={tipo}
          onChange={(e) => setTipo(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
        >
          <option value="LIGACAO">Ligação</option>
          <option value="WHATSAPP">WhatsApp</option>
          <option value="EMAIL">E-mail</option>
          <option value="PRESENCIAL">Presencial</option>
        </select>
        <input
          required
          placeholder="Registrar resumo da interação..."
          value={resumo}
          onChange={(e) => setResumo(e.target.value)}
          className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
        />
        <button type="submit" className="rounded-lg bg-slate-900 text-white px-4 py-1.5 text-sm font-medium">
          Registrar
        </button>
      </form>

      <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
        {itens.map((i) => (
          <div key={i.id} className="p-4 text-sm">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                {i.tipo}
              </span>
              <span className="text-xs text-slate-400">
                {i.usuario_nome} • {new Date(i.created_at).toLocaleString("pt-BR")}
              </span>
            </div>
            <p className="text-slate-800">{i.resumo}</p>
          </div>
        ))}
        {itens.length === 0 && (
          <div className="p-6 text-center text-sm text-slate-400">Nenhuma interação registrada.</div>
        )}
      </div>
    </div>
  );
}
