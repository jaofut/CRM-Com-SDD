"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser, getToken } from "@/lib/api";
import type { UsuarioResumo } from "@/types/auth";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    const user = getStoredUser<UsuarioResumo>();
    if (!token || !user) {
      router.replace("/login");
    } else {
      router.replace(user.perfil === "ADMIN" ? "/dashboard" : "/orcamentos");
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center text-sm text-slate-500">
      Carregando...
    </div>
  );
}
