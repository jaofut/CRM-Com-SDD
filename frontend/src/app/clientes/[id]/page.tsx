"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { MessageCircle, Plus, Truck, User, Users } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { ClienteTimeline } from "@/components/ClienteTimeline";
import { apiFetch } from "@/lib/api";

interface Contato {
  id: number;
  nome: string;
  cargo: string;
  telefone_whatsapp: string;
  email: string | null;
  principal: boolean;
}

interface Motorista {
  id: number;
  nome: string;
  telefone: string | null;
  documento: string | null;
  ativo: boolean;
}

interface Veiculo {
  id: number;
  placa: string;
  tipo: string;
  marca_modelo: string;
  ano: number | null;
  chassi: string | null;
  km_atual: number;
}

interface ClienteDetalhe {
  id: number;
  razao_social: string;
  nome_fantasia: string;
  cnpj: string;
  condicoes_comerciais: string | null;
  ativo: boolean;
  contatos: Contato[];
  motoristas: Motorista[];
  veiculos: Veiculo[];
}

export default function ClienteDetalhePage() {
  const params = useParams<{ id: string }>();
  const clienteId = params.id;
  const [cliente, setCliente] = useState<ClienteDetalhe | null>(null);
  const [tab, setTab] = useState<"veiculos" | "contatos" | "motoristas" | "timeline">("veiculos");

  // Forms
  const [placa, setPlaca] = useState("");
  const [tipo, setTipo] = useState("CAVALO_MECANICO");
  const [marcaModelo, setMarcaModelo] = useState("");
  const [kmAtual, setKmAtual] = useState("0");

  const [cNome, setCNome] = useState("");
  const [cCargo, setCCargo] = useState("Gestor de Frota");
  const [cZap, setCZap] = useState("");

  const [mNome, setMNome] = useState("");
  const [mTel, setMTel] = useState("");

  const [erro, setErro] = useState<string | null>(null);

  const load = useCallback(async () => {
    const data = await apiFetch<ClienteDetalhe>(`/clientes/${clienteId}`);
    setCliente(data);
  }, [clienteId]);

  useEffect(() => {
    load();
  }, [load]);

  async function addVeiculo(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch(`/clientes/${clienteId}/veiculos`, {
        method: "POST",
        body: JSON.stringify({
          placa,
          tipo,
          marca_modelo: marcaModelo,
          km_atual: Number(kmAtual) || 0,
        }),
      });
      setPlaca("");
      setMarcaModelo("");
      setKmAtual("0");
      await load();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao cadastrar veículo");
    }
  }

  async function addContato(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch(`/clientes/${clienteId}/contatos`, {
        method: "POST",
        body: JSON.stringify({
          nome: cNome,
          cargo: cCargo,
          telefone_whatsapp: cZap,
          principal: cliente?.contatos.length === 0,
        }),
      });
      setCNome("");
      setCZap("");
      await load();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao cadastrar contato");
    }
  }

  async function addMotorista(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    try {
      await apiFetch(`/clientes/${clienteId}/motoristas`, {
        method: "POST",
        body: JSON.stringify({ nome: mNome, telefone: mTel || null }),
      });
      setMNome("");
      setMTel("");
      await load();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao cadastrar motorista");
    }
  }

  if (!cliente) {
    return (
      <AppShell>
        <div className="text-sm text-slate-500">Carregando ficha da frota...</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{cliente.nome_fantasia}</h1>
            <p className="text-sm text-slate-500">
              {cliente.razao_social} • CNPJ: <span className="font-mono">{cliente.cnpj}</span>
            </p>
            {cliente.condicoes_comerciais && (
              <p className="text-xs text-slate-600 mt-2">
                Condições: {cliente.condicoes_comerciais}
              </p>
            )}
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">
            {cliente.ativo ? "Frota Ativa" : "Inativa"}
          </span>
        </div>
      </div>

      {erro && (
        <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-2 text-sm text-red-700">
          {erro}
        </div>
      )}

      <div className="flex gap-2 mb-4 border-b border-slate-200">
        {[
          { id: "veiculos", label: `Veículos (${cliente.veiculos.length})`, icon: Truck },
          { id: "contatos", label: `Contatos (${cliente.contatos.length})`, icon: Users },
          { id: "motoristas", label: `Motoristas (${cliente.motoristas.length})`, icon: User },
          { id: "timeline", label: "Timeline CRM", icon: MessageCircle },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id as typeof tab)}
              className={`inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px ${
                tab === t.id
                  ? "border-amber-500 text-slate-900"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              <Icon className="w-4 h-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {tab === "veiculos" && (
        <div className="space-y-4">
          <form onSubmit={addVeiculo} className="bg-white rounded-xl border border-slate-200 p-4 flex flex-wrap gap-2">
            <input
              required
              placeholder="Placa (ex.: ABC1D23)"
              value={placa}
              onChange={(e) => setPlaca(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-36"
            />
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
            >
              <option value="CAVALO_MECANICO">Cavalo Mecânico</option>
              <option value="CARRETA">Carreta</option>
              <option value="TRUCK">Truck</option>
              <option value="TOCO">Toco</option>
              <option value="ONIBUS">Ônibus</option>
              <option value="UTILITARIO_PESADO">Utilitário Pesado</option>
            </select>
            <input
              required
              placeholder="Marca / Modelo (ex.: Scania R450)"
              value={marcaModelo}
              onChange={(e) => setMarcaModelo(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm flex-1 min-w-48"
            />
            <input
              type="number"
              min={0}
              placeholder="KM Atual"
              value={kmAtual}
              onChange={(e) => setKmAtual(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-32"
            />
            <button
              type="submit"
              className="inline-flex items-center gap-1 rounded-lg bg-slate-900 text-white px-3 py-1.5 text-sm font-medium"
            >
              <Plus className="w-4 h-4" /> Adicionar Veículo
            </button>
          </form>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-2.5">Placa</th>
                  <th className="px-4 py-2.5">Tipo</th>
                  <th className="px-4 py-2.5">Marca / Modelo</th>
                  <th className="px-4 py-2.5">KM Atual</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {cliente.veiculos.map((v) => (
                  <tr key={v.id}>
                    <td className="px-4 py-2.5 font-mono font-semibold">{v.placa}</td>
                    <td className="px-4 py-2.5 text-slate-600">{v.tipo}</td>
                    <td className="px-4 py-2.5">{v.marca_modelo}</td>
                    <td className="px-4 py-2.5">{v.km_atual.toLocaleString("pt-BR")} km</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "contatos" && (
        <div className="space-y-4">
          <form onSubmit={addContato} className="bg-white rounded-xl border border-slate-200 p-4 flex flex-wrap gap-2">
            <input
              required
              placeholder="Nome"
              value={cNome}
              onChange={(e) => setCNome(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm flex-1"
            />
            <input
              required
              placeholder="Cargo"
              value={cCargo}
              onChange={(e) => setCCargo(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-44"
            />
            <input
              required
              placeholder="WhatsApp (DDD + número)"
              value={cZap}
              onChange={(e) => setCZap(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-48"
            />
            <button type="submit" className="rounded-lg bg-slate-900 text-white px-3 py-1.5 text-sm font-medium">
              Adicionar Contato
            </button>
          </form>

          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
            {cliente.contatos.map((c) => (
              <div key={c.id} className="p-4 flex items-center justify-between">
                <div>
                  <div className="font-medium text-slate-900">
                    {c.nome} {c.principal && <span className="text-xs text-amber-600 font-semibold">(Principal)</span>}
                  </div>
                  <div className="text-xs text-slate-500">{c.cargo} • {c.telefone_whatsapp}</div>
                </div>
                <a
                  href={`https://wa.me/55${c.telefone_whatsapp.replace(/\D/g, "")}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-medium text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg hover:bg-emerald-100"
                >
                  WhatsApp Web
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "motoristas" && (
        <div className="space-y-4">
          <form onSubmit={addMotorista} className="bg-white rounded-xl border border-slate-200 p-4 flex flex-wrap gap-2">
            <input
              required
              placeholder="Nome do Motorista"
              value={mNome}
              onChange={(e) => setMNome(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm flex-1"
            />
            <input
              placeholder="Telefone"
              value={mTel}
              onChange={(e) => setMTel(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm w-48"
            />
            <button type="submit" className="rounded-lg bg-slate-900 text-white px-3 py-1.5 text-sm font-medium">
              Adicionar Motorista
            </button>
          </form>

          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
            {cliente.motoristas.map((m) => (
              <div key={m.id} className="p-4 flex items-center justify-between text-sm">
                <div className="font-medium text-slate-900">{m.nome}</div>
                <div className="text-slate-500">{m.telefone || "Sem telefone"}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "timeline" && <ClienteTimeline clienteId={clienteId} />}
    </AppShell>
  );
}
