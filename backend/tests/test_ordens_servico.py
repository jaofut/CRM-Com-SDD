def test_conversao_orcamento_os_km_regressiva_e_entrega(client, atendente_headers):
    c = client.post(
        "/api/v1/clientes",
        json={
            "razao_social": "Rodoviário Sul Ltda",
            "nome_fantasia": "RodoSul",
            "cnpj": "22.333.444/0001-55",
        },
        headers=atendente_headers,
    ).json()
    contato = client.post(
        f"/api/v1/clientes/{c['id']}/contatos",
        json={"nome": "Pedro", "cargo": "Gerente", "telefone_whatsapp": "11966665555", "principal": True},
        headers=atendente_headers,
    ).json()
    mot = client.post(
        f"/api/v1/clientes/{c['id']}/motoristas",
        json={"nome": "José Silva"},
        headers=atendente_headers,
    ).json()
    veic = client.post(
        f"/api/v1/clientes/{c['id']}/veiculos",
        json={"placa": "DEF2G34", "tipo": "TRUCK", "marca_modelo": "MB Axor 2544", "km_atual": 200000},
        headers=atendente_headers,
    ).json()

    orc = client.post(
        "/api/v1/orcamentos",
        json={
            "cliente_id": c["id"],
            "contato_id": contato["id"],
            "veiculo_id": veic["id"],
            "itens": [
                {"tipo": "SERVICO", "descricao": "Revisão diferencial", "quantidade": "1", "valor_unitario": "1200.00"}
            ],
        },
        headers=atendente_headers,
    ).json()

    # Aprovar orçamento
    client.patch(
        f"/api/v1/orcamentos/{orc['id']}/etapa",
        json={"etapa": "APROVADO", "po_aprovacao": "PO-998"},
        headers=atendente_headers,
    )

    # Tentativa de converter com KM menor sem confirmação -> 422
    conv_fail = client.post(
        f"/api/v1/orcamentos/{orc['id']}/converter-os",
        json={"km_entrada": 190000, "confirmar_km_menor": False, "motorista_entrada_id": mot["id"]},
        headers=atendente_headers,
    )
    assert conv_fail.status_code == 422

    # Converter com KM válida -> 201
    conv_ok = client.post(
        f"/api/v1/orcamentos/{orc['id']}/converter-os",
        json={
            "km_entrada": 201500,
            "confirmar_km_menor": False,
            "motorista_entrada_id": mot["id"],
            "avarias_entrada": "Para-choque dianteiro riscado",
        },
        headers=atendente_headers,
    )
    assert conv_ok.status_code == 201
    os_data = conv_ok.json()
    assert os_data["valor_total"] == "1200.00"
    assert len(os_data["itens"]) == 1

    # Entrega sem motorista_saida_id -> 422
    ent_fail = client.patch(
        f"/api/v1/ordens-servico/{os_data['id']}/status",
        json={"status": "ENTREGUE"},
        headers=atendente_headers,
    )
    assert ent_fail.status_code == 422

    # Entrega válida -> 200 e gera PDF
    ent_ok = client.patch(
        f"/api/v1/ordens-servico/{os_data['id']}/status",
        json={"status": "ENTREGUE", "motorista_saida_id": mot["id"], "preventiva_dias": 90},
        headers=atendente_headers,
    )
    assert ent_ok.status_code == 200
    assert ent_ok.json()["status"] == "ENTREGUE"

    pdf = client.get(f"/api/v1/ordens-servico/{os_data['id']}/pdf", headers=atendente_headers)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
