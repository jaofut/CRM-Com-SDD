"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bell,
  Building2,
  ClipboardList,
  Kanban,
  LayoutDashboard,
  LogOut,
  Truck,
  Users,
} from "lucide-react";
import { clearAuthSession, getStoredUser, getToken } from "@/lib/api";
import type { UsuarioResumo } from "@/types/auth";
import { GlobalSearch } from "@/components/GlobalSearch";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UsuarioResumo | null>(null);

  useEffect(() => {
    const token = getToken();
    const stored = getStoredUser<UsuarioResumo>();
    if (!token || !stored) {
      router.replace("/login");
      return;
    }
    setUser(stored);
  }, [router]);

  function handleLogout() {
    clearAuthSession();
    router.replace("/login");
  }

  const navItems = [
    ...(user?.perfil === "ADMIN"
      ? [{ href: "/dashboard", label: "Dashboard", icon: LayoutDashboard }]
      : []),
    { href: "/clientes", label: "Frotas & Clientes", icon: Building2 },
    { href: "/orcamentos", label: "Orçamentos", icon: Kanban },
    { href: "/os", label: "Ordens de Serviço", icon: ClipboardList },
    { href: "/lembretes", label: "Preventivas & Follow-up", icon: Bell },
    ...(user?.perfil === "ADMIN"
      ? [{ href: "/usuarios", label: "Usuários", icon: Users }]
      : []),
  ];

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-slate-500">
        Verificando sessão...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-800 flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-amber-500 text-slate-950">
            <Truck className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold text-sm leading-tight">Oficina Pesados</div>
            <div className="text-[11px] text-slate-400">CRM B2B &amp; Frotas</div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition ${
                  active
                    ? "bg-amber-500 text-slate-950 font-semibold"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-slate-800 text-xs">
          <div className="px-2 py-1 mb-2">
            <div className="font-medium text-white truncate">{user.nome}</div>
            <div className="text-slate-400">{user.perfil}</div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            <LogOut className="w-4 h-4" />
            Sair
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between gap-4">
          <GlobalSearch />
          <div className="text-xs text-slate-500 hidden sm:block">
            {user.email}
          </div>
        </header>
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
