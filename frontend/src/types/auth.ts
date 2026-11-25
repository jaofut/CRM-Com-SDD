export type PerfilUsuario = "ADMIN" | "ATENDENTE";

export interface UsuarioResumo {
  id: number;
  nome: string;
  email: string;
  perfil: PerfilUsuario;
  ativo: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  usuario: UsuarioResumo;
}
