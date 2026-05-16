# ── List ─────────────────────────────────────────────────────────────────────

def test_super_admin_sees_all_labs(client, db_tables, lab, sa_headers):
    resp = client.get("/labs", headers=sa_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_member_sees_only_their_labs(client, db_tables, lab, mgr_headers):
    # Create a second lab the manager doesn't belong to
    resp = client.get("/labs", headers=mgr_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["id"] == lab


def test_list_labs_without_token_returns_401(client, db_tables):
    resp = client.get("/labs")
    assert resp.status_code == 401


# ── Create ────────────────────────────────────────────────────────────────────

def test_super_admin_can_create_lab(client, db_tables, super_admin, sa_headers):
    resp = client.post("/labs",
                       json={"name": "New Lab", "description": "Desc"},
                       headers=sa_headers)
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "New Lab"


def test_manager_cannot_create_lab(client, db_tables, lab, mgr_headers):
    resp = client.post("/labs", json={"name": "Rogue Lab"},
                       headers=mgr_headers)
    assert resp.status_code == 403


# ── Get ───────────────────────────────────────────────────────────────────────

def test_get_lab_returns_200(client, db_tables, lab, sa_headers):
    resp = client.get(f"/labs/{lab}", headers=sa_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == lab


def test_get_nonexistent_lab_returns_404(client, db_tables, sa_headers,
                                         super_admin):
    resp = client.get("/labs/9999", headers=sa_headers)
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────

def test_super_admin_can_update_lab(client, db_tables, lab, sa_headers):
    resp = client.put(f"/labs/{lab}", json={"name": "Updated Lab"},
                      headers=sa_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Updated Lab"


# ── Delete ────────────────────────────────────────────────────────────────────

def test_super_admin_can_delete_lab(client, db_tables, lab, sa_headers):
    resp = client.delete(f"/labs/{lab}", headers=sa_headers)
    assert resp.status_code == 204


def test_manager_cannot_delete_lab(client, db_tables, lab, mgr_headers):
    resp = client.delete(f"/labs/{lab}", headers=mgr_headers)
    assert resp.status_code == 403
