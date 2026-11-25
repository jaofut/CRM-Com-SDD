"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Plus, Search } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface ClienteResumo {
  id: number;
  razao_social: string;
  nome_fantasia: string;
  cnpj: string;
  ativo: boolean;
}

export default function ClientesPage() {
  const [clientes, setClientes] = useState<ClienteResumo[]>([]);
  const [q, setQ] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [razaoSocial, setRazaoSocial] = useState("");
  const [nomeFantasia, setNomeFantasia] = useState("");
  const [cnpj, setCnpj] = useState("");
  const [condicoes, setCondicoes] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function load(search = "") {
    const query = search ? `?q=${encodeURIComponent(search)}` : "";
    const data = await apiFetch<ClienteResumo[]>(`/clientes${query}`);
    setClientes(data);
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch("/clientes", {
        method: "POST",
        body: JSON.stringify({
          razao_social: razaoSocial,
          nome_fantasia: nomeFantasia,
          cnpj,
          condicoes_comerciais: condicoes || null,
        }),
      });
      setShowModal(false);
      setRazaoSocial("");
      setNomeFantasia("");
      setCnpj("");
      setCondicoes("");
      await load(q);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao cadastrar");
    }
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Frotas &amp; Clientes B2B</h1>
          <p className="text-sm text-slate-500">Transportadoras, contatos, motoristas e veículos</p>
        </div>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-slate-900 text-white px-4 py-2 text-sm font-medium hover:bg-slate-800"
        >
          <Plus className="w-4 h-4" />
          Nova Frota
        </button>
      </div>

      <div className="mb-4 flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              load(e.target.value);
            }}
            placeholder="Filtrar por nome ou CNPJ..."
            className="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 py-2 text-sm"
          />
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Nome Fantasia</th>
              <th className="px-4 py-3 font-medium">Razão Social</th>
              <th className="px-4 py-3 font-medium">CNPJ</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {clientes.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium text-slate-900 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-amber-600" />
                  {c.nome_fantasia}
                </td>
                <td className="px-4 py-3 text-slate-600">{c.razao_social}</td>
                <td className="px-4 py-3 text-slate-600 font-mono text-xs">{c.cnpj}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                      c.ativo ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {c.ativo ? "Ativo" : "Inativo"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/clientes/${c.id}`}
                    className="text-amber-600 hover:text-amber-700 font-medium"
                  >
                    Abrir ficha →
                  </Link>
                </td>
              </tr>
            ))}
            {clientes.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                  Nenhuma transportadora cadastrada.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <h2 className="text-lg font-bold mb-4">Cadastrar Frota / Transportadora</h2>
            <form onSubmit={handleCreate} className="space-y-3">
              <input
                required
                placeholder="Razão Social"
                value={razaoSocial}
                onChange={(e) => setRazaoSocial(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <input
                required
                placeholder="Nome Fantasia"
                value={nomeFantasia}
                onChange={(e) => setNomeFantasia(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <input
                required
                placeholder="CNPJ"
                value={cnpj}
                onChange={(e) => setCnpj(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <textarea
                placeholder="Condições comerciais (ex.: Faturamento 28 dias)"
                value={condicoes}
                onChange={(e) => setCondicoes(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                rows={2}
              />
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
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
