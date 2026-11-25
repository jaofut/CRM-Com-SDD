def test_rbac_usuarios_e_dashboard(client, admin_headers, atendente_headers):
    # Atendente bloqueado em /usuarios e /dashboard/gerencial (403)
    assert client.get("/api/v1/usuarios", headers=atendente_headers).status_code == 403
    assert client.get("/api/v1/dashboard/gerencial", headers=atendente_headers).status_code == 403

    # Admin cria novo atendente
    novo = client.post(
        "/api/v1/usuarios",
        json={
            "nome": "Novo Consultor",
            "email": "consultor@oficina.com",
            "senha": "secret123",
            "perfil": "ATENDENTE",
        },
        headers=admin_headers,
    )
    assert novo.status_code == 201
    uid = novo.json()["id"]

    # Login funciona
    login_ok = client.post(
        "/api/v1/auth/login",
        json={"email": "consultor@oficina.com", "senha": "secret123"},
    )
    assert login_ok.status_code == 200

    # Admin desativa usuário -> login bloqueado
    deact = client.patch(
        f"/api/v1/usuarios/{uid}",
        json={"ativo": False},
        headers=admin_headers,
    )
    assert deact.status_code == 200
    assert deact.json()["ativo"] is False

    login_fail = client.post(
        "/api/v1/auth/login",
        json={"email": "consultor@oficina.com", "senha": "secret123"},
    )
    assert login_fail.status_code == 401

    # Admin acessa dashboard gerencial
    dash = client.get("/api/v1/dashboard/gerencial", headers=admin_headers)
    assert dash.status_code == 200
    assert "taxa_conversao_percent" in dash.json()
    assert "os_por_status" in dash.json()
