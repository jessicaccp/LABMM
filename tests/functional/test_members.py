# ── List members ─────────────────────────────────────────────────────────────

def test_any_lab_member_can_list_members(client, db_tables, lab, stf_headers):
    resp = client.get(f"/labs/{lab}/members", headers=stf_headers)
    assert resp.status_code == 200


def test_list_members_without_token_returns_401(client, db_tables, lab):
    resp = client.get(f"/labs/{lab}/members")
    assert resp.status_code == 401


def test_non_member_cannot_list_members(client, db_tables, lab, super_admin,
                                         sa_headers):
    # Create a member not assigned to the lab
    r = client.post("/auth/register",
                    json={"first_name": "Outsider", "last_name": "X",
                          "email": "out@lab.local", "password": "pass"},
                    headers=sa_headers)
    outsider_id = r.get_json()["member"]["id"]
    from flask_jwt_extended import create_access_token
    with client.application.app_context():
        token = create_access_token(identity=str(outsider_id),
                                    additional_claims={"is_super_admin": False})
    resp = client.get(f"/labs/{lab}/members",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


# ── Add member ────────────────────────────────────────────────────────────────

def test_manager_can_add_member(client, db_tables, lab, super_admin,
                                 sa_headers, mgr_headers):
    r = client.post("/auth/register",
                    json={"first_name": "New", "last_name": "Guy",
                          "email": "new@lab.local", "password": "pass"},
                    headers=sa_headers)
    new_id = r.get_json()["member"]["id"]
    resp = client.post(f"/labs/{lab}/members",
                       json={"member_id": new_id, "role": "researcher"},
                       headers=mgr_headers)
    assert resp.status_code == 201
    assert resp.get_json()["role"] == "researcher"


def test_researcher_cannot_add_member(client, db_tables, lab, super_admin,
                                       sa_headers, res_headers):
    r = client.post("/auth/register",
                    json={"first_name": "New2", "last_name": "Guy",
                          "email": "new2@lab.local", "password": "pass"},
                    headers=sa_headers)
    new_id = r.get_json()["member"]["id"]
    resp = client.post(f"/labs/{lab}/members",
                       json={"member_id": new_id, "role": "staff"},
                       headers=res_headers)
    assert resp.status_code == 403


def test_add_duplicate_member_returns_409(client, db_tables, lab, manager,
                                           mgr_headers):
    resp = client.post(f"/labs/{lab}/members",
                       json={"member_id": manager, "role": "manager"},
                       headers=mgr_headers)
    assert resp.status_code == 409


# ── Update role ───────────────────────────────────────────────────────────────

def test_manager_can_update_member_role(client, db_tables, lab, researcher,
                                         mgr_headers):
    resp = client.put(f"/labs/{lab}/members/{researcher}",
                      json={"role": "engineer"},
                      headers=mgr_headers)
    assert resp.status_code == 200
    assert resp.get_json()["role"] == "engineer"


# ── Remove member ─────────────────────────────────────────────────────────────

def test_manager_can_remove_member(client, db_tables, lab, researcher,
                                    mgr_headers):
    resp = client.delete(f"/labs/{lab}/members/{researcher}",
                         headers=mgr_headers)
    assert resp.status_code == 204


def test_engineer_cannot_remove_member(client, db_tables, lab, researcher,
                                        eng_headers):
    resp = client.delete(f"/labs/{lab}/members/{researcher}",
                         headers=eng_headers)
    assert resp.status_code == 403


# ── Own profile update ────────────────────────────────────────────────────────

def test_member_can_update_own_profile(client, db_tables, researcher,
                                        res_headers):
    resp = client.put(f"/members/{researcher}",
                      json={"first_name": "Updated"},
                      headers=res_headers)
    assert resp.status_code == 200
    assert resp.get_json()["first_name"] == "Updated"


def test_member_cannot_update_others_profile(client, db_tables, researcher,
                                              engineer, eng_headers):
    resp = client.put(f"/members/{researcher}",
                      json={"first_name": "Hacked"},
                      headers=eng_headers)
    assert resp.status_code == 403
