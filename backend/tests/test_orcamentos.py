def test_orcamento_calculo_recusa_e_pdf(client, atendente_headers):
    c = client.post(
        "/api/v1/clientes",
        json={
            "razao_social": "TransLog Pesados Ltda",
            "nome_fantasia": "TransLog",
            "cnpj": "11.222.333/0001-44",
        },
        headers=atendente_headers,
    ).json()
    contato = client.post(
        f"/api/v1/clientes/{c['id']}/contatos",
        json={
            "nome": "Mariana Frota",
            "cargo": "Gestora",
            "telefone_whatsapp": "11977776666",
            "principal": True,
        },
        headers=atendente_headers,
    ).json()
    veic = client.post(
        f"/api/v1/clientes/{c['id']}/veiculos",
        json={
            "placa": "XYZ9K88",
            "tipo": "CARRETA",
            "marca_modelo": "Randon Graneleira",
            "km_atual": 95000,
        },
        headers=atendente_headers,
    ).json()

    # Criar orçamento: (2 * 500) + (1 * 350) - 50 = 1300.00
    orc = client.post(
        "/api/v1/orcamentos",
        json={
            "cliente_id": c["id"],
            "contato_id": contato["id"],
            "veiculo_id": veic["id"],
            "desconto_total": "50.00",
            "itens": [
                {"tipo": "PECA", "descricao": "Jogo de Lona de Freio", "quantidade": "2", "valor_unitario": "500.00"},
                {"tipo": "SERVICO", "descricao": "Mão de obra freios", "quantidade": "1", "valor_unitario": "350.00"},
            ],
        },
        headers=atendente_headers,
    )
    assert orc.status_code == 201
    data = orc.json()
    assert data["etapa"] == "RASCUNHO"
    assert data["valor_total"] == "1300.00"

    # Recusa sem motivo -> 422
    rec_sem = client.patch(
        f"/api/v1/orcamentos/{data['id']}/etapa",
        json={"etapa": "RECUSADO"},
        headers=atendente_headers,
    )
    assert rec_sem.status_code == 422

    # Recusa com motivo -> 200
    rec_ok = client.patch(
        f"/api/v1/orcamentos/{data['id']}/etapa",
        json={"etapa": "RECUSADO", "motivo_recusa": "Preço acima do concorrente"},
        headers=atendente_headers,
    )
    assert rec_ok.status_code == 200
    assert rec_ok.json()["motivo_recusa"] == "Preço acima do concorrente"

    # PDF válido
    pdf = client.get(f"/api/v1/orcamentos/{data['id']}/pdf", headers=atendente_headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")
