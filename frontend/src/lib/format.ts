export function normalizePlaca(placa: string): string {
  return placa.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
}

export function buildWhatsAppLink(phone: string, message: string): string {
  const digits = phone.replace(/\D/g, "");
  return `https://wa.me/55${digits}?text=${encodeURIComponent(message)}`;
}
