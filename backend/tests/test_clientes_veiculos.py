def test_cadastro_frota_unicidade_e_busca(client, atendente_headers):
    # 1. Cadastrar transportadora
    resp = client.post(
        "/api/v1/clientes",
        json={
            "razao_social": "Transportadora Alpha Ltda",
            "nome_fantasia": "Alpha Cargas",
            "cnpj": "12.345.678/0001-90",
            "condicoes_comerciais": "Faturamento 28 dias",
        },
        headers=atendente_headers,
    )
    assert resp.status_code == 201
    cliente_id = resp.json()["id"]

    # 2. Bloquear CNPJ duplicado (409)
    dup = client.post(
        "/api/v1/clientes",
        json={
            "razao_social": "Outra Empresa",
            "nome_fantasia": "Outra",
            "cnpj": "12345678000190",
        },
        headers=atendente_headers,
    )
    assert dup.status_code == 409

    # 3. Adicionar contato e motorista
    c_resp = client.post(
        f"/api/v1/clientes/{cliente_id}/contatos",
        json={
            "nome": "Carlos Gestor",
            "cargo": "Gestor de Frota",
            "telefone_whatsapp": "11999990000",
            "principal": True,
        },
        headers=atendente_headers,
    )
    assert c_resp.status_code == 201

    m_resp = client.post(
        f"/api/v1/clientes/{cliente_id}/motoristas",
        json={"nome": "João Motorista", "telefone": "11988887777"},
        headers=atendente_headers,
    )
    assert m_resp.status_code == 201

    # 4. Cadastrar veículo
    v_resp = client.post(
        f"/api/v1/clientes/{cliente_id}/veiculos",
        json={
            "placa": "ABC-1D23",
            "tipo": "CAVALO_MECANICO",
            "marca_modelo": "Scania R450",
            "ano": 2022,
            "km_atual": 180000,
        },
        headers=atendente_headers,
    )
    assert v_resp.status_code == 201
    veiculo_id = v_resp.json()["id"]
    assert v_resp.json()["placa"] == "ABC1D23"

    # 5. Bloquear placa duplicada (409)
    v_dup = client.post(
        f"/api/v1/clientes/{cliente_id}/veiculos",
        json={
            "placa": "abc1d23",
            "tipo": "TRUCK",
            "marca_modelo": "Volvo FH",
            "km_atual": 1000,
        },
        headers=atendente_headers,
    )
    assert v_dup.status_code == 409

    # 6. Busca global por placa e CNPJ
    busca_placa = client.get("/api/v1/busca?q=ABC1D23", headers=atendente_headers)
    assert busca_placa.status_code == 200
    assert len(busca_placa.json()["veiculos"]) == 1

    busca_cnpj = client.get("/api/v1/busca?q=12345678", headers=atendente_headers)
    assert busca_cnpj.status_code == 200
    assert len(busca_cnpj.json()["clientes"]) == 1

    # 7. Transferência de veículo para outra frota
    c2 = client.post(
        "/api/v1/clientes",
        json={
            "razao_social": "Beta Logística SA",
            "nome_fantasia": "Beta Log",
            "cnpj": "98.765.432/0001-10",
        },
        headers=atendente_headers,
    ).json()
    transf = client.patch(
        f"/api/v1/veiculos/{veiculo_id}",
        json={"cliente_id": c2["id"]},
        headers=atendente_headers,
    )
    assert transf.status_code == 200
    assert transf.json()["cliente_id"] == c2["id"]
