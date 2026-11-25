from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def gerar_pdf_orcamento(orc) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"ORÇAMENTO {orc.numero}")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, y, f"Etapa: {orc.etapa.value} | Validade: {orc.validade_dias} dias")
    y -= 28

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Dados da Frota / Veículo")
    y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Cliente: {orc.cliente.nome_fantasia} (CNPJ: {orc.cliente.cnpj})")
    y -= 14
    c.drawString(40, y, f"Contato: {orc.contato.nome} ({orc.contato.telefone_whatsapp})")
    y -= 14
    c.drawString(40, y, f"Veículo: {orc.veiculo.placa} - {orc.veiculo.marca_modelo} ({orc.veiculo.km_atual} km)")
    y -= 24

    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Tipo")
    c.drawString(100, y, "Descrição")
    c.drawRightString(410, y, "Qtd")
    c.drawRightString(480, y, "Unit.")
    c.drawRightString(width - 40, y, "Subtotal")
    y -= 8
    c.line(40, y, width - 40, y)
    y -= 16

    c.setFont("Helvetica", 9.5)
    for item in orc.itens:
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9.5)
        c.drawString(40, y, item.tipo.value)
        c.drawString(100, y, item.descricao[:48])
        c.drawRightString(410, y, f"{item.quantidade:.2f}")
        c.drawRightString(480, y, f"R$ {item.valor_unitario:.2f}")
        c.drawRightString(width - 40, y, f"R$ {item.subtotal:.2f}")
        y -= 15

    y -= 10
    c.line(40, y, width - 40, y)
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, y, f"Desconto: R$ {orc.desconto_total:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 40, y, f"TOTAL: R$ {orc.valor_total:.2f}")

    if orc.observacoes:
        y -= 28
        c.setFont("Helvetica", 9)
        c.drawString(40, y, f"Observações: {orc.observacoes[:100]}")

    c.showPage()
    c.save()
    return buf.getvalue()


def gerar_pdf_os(os_obj) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"ORDEM DE SERVIÇO {os_obj.numero}")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, y, f"Status: {os_obj.status.value}")
    y -= 28

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Frota / Veículo / Checklist")
    y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Cliente: {os_obj.cliente.nome_fantasia} (CNPJ: {os_obj.cliente.cnpj})")
    y -= 14
    c.drawString(40, y, f"Veículo: {os_obj.veiculo.placa} - {os_obj.veiculo.marca_modelo} | KM Entrada: {os_obj.km_entrada}")
    y -= 14
    mot_ent = os_obj.motorista_entrada.nome if os_obj.motorista_entrada else "Não informado"
    mot_sai = os_obj.motorista_saida.nome if os_obj.motorista_saida else "Pendente"
    c.drawString(40, y, f"Entregue por: {mot_ent} | Retirado por: {mot_sai}")
    y -= 14
    if os_obj.avarias_entrada:
        c.drawString(40, y, f"Avarias Entrada: {os_obj.avarias_entrada[:90]}")
        y -= 14
    y -= 12

    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Tipo")
    c.drawString(100, y, "Descrição")
    c.drawRightString(410, y, "Qtd")
    c.drawRightString(480, y, "Unit.")
    c.drawRightString(width - 40, y, "Subtotal")
    y -= 8
    c.line(40, y, width - 40, y)
    y -= 16

    c.setFont("Helvetica", 9.5)
    for item in os_obj.itens:
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9.5)
        c.drawString(40, y, item.tipo.value)
        c.drawString(100, y, item.descricao[:48])
        c.drawRightString(410, y, f"{item.quantidade:.2f}")
        c.drawRightString(480, y, f"R$ {item.valor_unitario:.2f}")
        c.drawRightString(width - 40, y, f"R$ {item.subtotal:.2f}")
        y -= 15

    y -= 10
    c.line(40, y, width - 40, y)
    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 40, y, f"TOTAL OS: R$ {os_obj.valor_total:.2f}")

    c.showPage()
    c.save()
    return buf.getvalue()
