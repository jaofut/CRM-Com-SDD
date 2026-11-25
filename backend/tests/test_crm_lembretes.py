def test_timeline_e_preventivas(client, atendente_headers):
    c = client.post(
        "/api/v1/clientes",
        json={
            "razao_social": "Expresso Norte Ltda",
            "nome_fantasia": "Expresso Norte",
            "cnpj": "33.444.555/0001-66",
        },
        headers=atendente_headers,
    ).json()
    mot = client.post(
        f"/api/v1/clientes/{c['id']}/motoristas",
        json={"nome": "Marcos Condutor"},
        headers=atendente_headers,
    ).json()
    veic = client.post(
        f"/api/v1/clientes/{c['id']}/veiculos",
        json={"placa": "GHI3J45", "tipo": "ONIBUS", "marca_modelo": "Marcopolo G8", "km_atual": 100000},
        headers=atendente_headers,
    ).json()

    # Registrar interação manual
    inter = client.post(
        f"/api/v1/clientes/{c['id']}/interacoes",
        json={"tipo": "LIGACAO", "resumo": "Contato inicial para revisão de freios"},
        headers=atendente_headers,
    )
    assert inter.status_code == 201

    # Abrir OS direta e entregar -> gera lembrete preventivo e evento na timeline
    os_resp = client.post(
        "/api/v1/ordens-servico",
        json={
            "cliente_id": c["id"],
            "veiculo_id": veic["id"],
            "km_entrada": 100500,
            "motorista_entrada_id": mot["id"],
            "itens": [{"tipo": "SERVICO", "descricao": "Troca óleo", "quantidade": "1", "valor_unitario": "450.00"}],
        },
        headers=atendente_headers,
    ).json()

    client.patch(
        f"/api/v1/ordens-servico/{os_resp['id']}/status",
        json={
            "status": "ENTREGUE",
            "motorista_saida_id": mot["id"],
            "preventiva_dias": 60,
            "km_previsto_proxima_revisao": 115000,
        },
        headers=atendente_headers,
    )

    timeline = client.get(f"/api/v1/clientes/{c['id']}/interacoes", headers=atendente_headers).json()
    assert len(timeline) == 2

    lembretes = client.get("/api/v1/lembretes?status=PENDENTE", headers=atendente_headers).json()
    assert len(lembretes) == 1
    assert lembretes[0]["tipo"] == "PREVENTIVA"
    assert lembretes[0]["km_previsto"] == 115000

    # Concluir lembrete
    done = client.patch(
        f"/api/v1/lembretes/{lembretes[0]['id']}",
        json={"status": "CONCLUIDO"},
        headers=atendente_headers,
    )
    assert done.status_code == 200
    assert done.json()["status"] == "CONCLUIDO"
