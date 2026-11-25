import { describe, expect, it } from "vitest";
import { buildWhatsAppLink, normalizePlaca } from "./format";

describe("format helpers", () => {
  it("normalizes heavy vehicle plates", () => {
    expect(normalizePlaca("abc-1d23")).toBe("ABC1D23");
  });

  it("builds wa.me link with encoded message", () => {
    const url = buildWhatsAppLink("(11) 99999-0000", "Olá frota");
    expect(url).toBe("https://wa.me/5511999990000?text=Ol%C3%A1%20frota");
  });
});
