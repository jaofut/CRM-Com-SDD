"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";
import type { UsuarioResumo } from "@/types/auth";

export default function UsuariosPage() {
  const [usuarios, setUsuarios] = useState<UsuarioResumo[]>([]);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState<"ADMIN" | "ATENDENTE">("ATENDENTE");
  const [erro, setErro] = useState<string | null>(null);

  async function load() {
    try {
      const data = await apiFetch<UsuarioResumo[]>("/usuarios");
      setUsuarios(data);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Acesso restrito");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch("/usuarios", {
        method: "POST",
        body: JSON.stringify({ nome, email, senha, perfil }),
      });
      setNome("");
      setEmail("");
      setSenha("");
      await load();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao criar usuário");
    }
  }

  async function toggleAtivo(u: UsuarioResumo) {
    await apiFetch(`/usuarios/${u.id}`, {
      method: "PATCH",
      body: JSON.stringify({ ativo: !u.ativo }),
    });
    await load();
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Usuários do Sistema</h1>
        <p className="text-sm text-slate-500">Controle de acesso (Administrador/Gerente e Atendente/Consultor)</p>
      </div>

      <form onSubmit={handleCreate} className="bg-white rounded-xl border border-slate-200 p-4 mb-6 flex flex-wrap gap-2">
        <input
          required
          placeholder="Nome"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm flex-1"
        />
        <input
          type="email"
          required
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-56"
        />
        <input
          type="password"
          required
          minLength={6}
          placeholder="Senha (mín. 6)"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-40"
        />
        <select
          value={perfil}
          onChange={(e) => setPerfil(e.target.value as "ADMIN" | "ATENDENTE")}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
        >
          <option value="ATENDENTE">Atendente/Consultor</option>
          <option value="ADMIN">Administrador/Gerente</option>
        </select>
        <button type="submit" className="rounded-lg bg-slate-900 text-white px-4 py-1.5 text-sm font-medium">
          Criar Usuário
        </button>
      </form>

      {erro && <p className="text-sm text-red-600 mb-4">{erro}</p>}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3">Nome</th>
              <th className="px-4 py-3">E-mail</th>
              <th className="px-4 py-3">Perfil</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Ação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {usuarios.map((u) => (
              <tr key={u.id}>
                <td className="px-4 py-3 font-medium">{u.nome}</td>
                <td className="px-4 py-3 text-slate-600">{u.email}</td>
                <td className="px-4 py-3 text-xs font-semibold">{u.perfil}</td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs ${
                      u.ativo ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {u.ativo ? "Ativo" : "Inativo"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    onClick={() => toggleAtivo(u)}
                    className="text-xs font-medium text-amber-600 hover:text-amber-700"
                  >
                    {u.ativo ? "Desativar" : "Reativar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
