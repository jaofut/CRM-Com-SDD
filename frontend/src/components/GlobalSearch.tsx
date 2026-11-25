"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search, Truck, Building2 } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface BuscaResult {
  clientes: { id: number; nome_fantasia: string; razao_social: string; cnpj: string }[];
  veiculos: { id: number; placa: string; marca_modelo: string; cliente_id: number; cliente_nome: string }[];
}

export function GlobalSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<BuscaResult | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResults(null);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const data = await apiFetch<BuscaResult>(`/busca?q=${encodeURIComponent(trimmed)}`);
        setResults(data);
        setOpen(true);
      } catch {
        setResults(null);
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="relative w-full max-w-md">
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={query}
          onFocus={() => results && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 180)}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar por CNPJ, Razão Social ou Placa..."
          className="w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 py-1.5 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500"
        />
      </div>

      {open && results && (results.clientes.length > 0 || results.veiculos.length > 0) && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg max-h-80 overflow-auto">
          {results.clientes.length > 0 && (
            <div className="p-2 border-b border-slate-100">
              <div className="text-[11px] font-semibold uppercase text-slate-400 px-2 pb-1">Frotas / Clientes</div>
              {results.clientes.map((c) => (
                <Link
                  key={`c-${c.id}`}
                  href={`/clientes/${c.id}`}
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-50 text-sm"
                >
                  <Building2 className="w-4 h-4 text-amber-600 shrink-0" />
                  <div className="truncate">
                    <div className="font-medium text-slate-800 truncate">{c.nome_fantasia}</div>
                    <div className="text-xs text-slate-500">{c.cnpj}</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
          {results.veiculos.length > 0 && (
            <div className="p-2">
              <div className="text-[11px] font-semibold uppercase text-slate-400 px-2 pb-1">Veículos</div>
              {results.veiculos.map((v) => (
                <button
                  key={`v-${v.id}`}
                  type="button"
                  onMouseDown={() => {
                    setOpen(false);
                    router.push(`/clientes/${v.cliente_id}`);
                  }}
                  className="w-full text-left flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-50 text-sm"
                >
                  <Truck className="w-4 h-4 text-slate-600 shrink-0" />
                  <div className="truncate">
                    <div className="font-medium text-slate-800">{v.placa} — {v.marca_modelo}</div>
                    <div className="text-xs text-slate-500 truncate">{v.cliente_nome}</div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
