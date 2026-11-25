"use client";

import { FileDown, MessageCircle, ArrowRightCircle } from "lucide-react";
import { downloadPdf } from "@/lib/api";

export interface OrcamentoItem {
  id: number;
  tipo: "PECA" | "SERVICO";
  descricao: string;
  quantidade: string;
  valor_unitario: string;
  subtotal: string;
}

export interface OrcamentoCard {
  id: number;
  numero: string;
  cliente_id: number;
  veiculo_id: number;
  etapa: "RASCUNHO" | "ENVIADO" | "EM_NEGOCIACAO" | "APROVADO" | "RECUSADO";
  valor_total: string;
  po_aprovacao: string | null;
  motivo_recusa: string | null;
  cliente_nome: string | null;
  veiculo_placa: string | null;
  contato_nome: string | null;
  contato_whatsapp: string | null;
  itens: OrcamentoItem[];
}

const ETAPAS: { key: OrcamentoCard["etapa"]; label: string; color: string }[] = [
  { key: "RASCUNHO", label: "Rascunho", color: "border-t-slate-400" },
  { key: "ENVIADO", label: "Enviado", color: "border-t-blue-500" },
  { key: "EM_NEGOCIACAO", label: "Em Negociação", color: "border-t-amber-500" },
  { key: "APROVADO", label: "Aprovado", color: "border-t-emerald-500" },
  { key: "RECUSADO", label: "Recusado", color: "border-t-red-500" },
];

interface Props {
  orcamentos: OrcamentoCard[];
  onMoverEtapa: (orc: OrcamentoCard, novaEtapa: OrcamentoCard["etapa"]) => void;
  onConverterOs: (orc: OrcamentoCard) => void;
}

export function OrcamentoKanban({ orcamentos, onMoverEtapa, onConverterOs }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-4 items-start">
      {ETAPAS.map((col) => {
        const cards = orcamentos.filter((o) => o.etapa === col.key);
        return (
          <div
            key={col.key}
            className={`bg-slate-100 rounded-xl p-3 border-t-4 ${col.color} min-h-[300px]`}
          >
            <div className="flex items-center justify-between mb-3 px-1">
              <span className="text-xs font-bold uppercase text-slate-700">{col.label}</span>
              <span className="text-xs bg-white px-2 py-0.5 rounded-full text-slate-600 font-medium">
                {cards.length}
              </span>
            </div>

            <div className="space-y-3">
              {cards.map((orc) => {
                const zapNum = orc.contato_whatsapp?.replace(/\D/g, "") || "";
                const zapMsg = encodeURIComponent(
                  `Olá ${orc.contato_nome || ""}, segue o orçamento ${orc.numero} para o veículo ${orc.veiculo_placa || ""} no valor total de R$ ${Number(orc.valor_total).toFixed(2)}.`
                );

                return (
                  <div
                    key={orc.id}
                    className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-slate-900">{orc.numero}</span>
                      <span className="text-xs font-mono bg-slate-100 px-1.5 py-0.5 rounded">
                        {orc.veiculo_placa}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-slate-800 truncate">
                      {orc.cliente_nome}
                    </div>
                    <div className="text-sm font-bold text-slate-900">
                      R$ {Number(orc.valor_total).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </div>
                    {orc.motivo_recusa && (
                      <div className="text-xs text-red-600 bg-red-50 rounded p-1.5">
                        Motivo: {orc.motivo_recusa}
                      </div>
                    )}

                    <div className="flex flex-wrap gap-1.5 pt-1 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => downloadPdf(`/orcamentos/${orc.id}/pdf`, `${orc.numero}.pdf`)}
                        className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700"
                      >
                        <FileDown className="w-3.5 h-3.5" /> PDF
                      </button>

                      {zapNum && (
                        <a
                          href={`https://wa.me/55${zapNum}?text=${zapMsg}`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-emerald-50 hover:bg-emerald-100 text-emerald-700"
                        >
                          <MessageCircle className="w-3.5 h-3.5" /> WhatsApp
                        </a>
                      )}

                      {orc.etapa === "APROVADO" && (
                        <button
                          type="button"
                          onClick={() => onConverterOs(orc)}
                          className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold"
                        >
                          <ArrowRightCircle className="w-3.5 h-3.5" /> Converter OS
                        </button>
                      )}
                    </div>

                    <select
                      value={orc.etapa}
                      onChange={(e) =>
                        onMoverEtapa(orc, e.target.value as OrcamentoCard["etapa"])
                      }
                      className="w-full mt-1 text-xs rounded border border-slate-200 px-2 py-1 bg-slate-50"
                    >
                      {ETAPAS.map((opt) => (
                        <option key={opt.key} value={opt.key}>
                          Mover para: {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
