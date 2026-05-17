# ── List ─────────────────────────────────────────────────────────────────────

def test_any_member_can_list_projects(client, db_tables, lab, stf_headers):
    resp = client.get(f"/labs/{lab}/projects", headers=stf_headers)
    assert resp.status_code == 200


def test_list_projects_without_token_returns_401(client, db_tables, lab):
    resp = client.get(f"/labs/{lab}/projects")
    assert resp.status_code == 401


# ── Create ────────────────────────────────────────────────────────────────────

def test_manager_can_create_project(client, db_tables, lab, manager, mgr_headers):
    resp = client.post(f"/labs/{lab}/projects",
                       json={"name": "Project X", "status": "planned",
                             "tech_lead_id": manager},
                       headers=mgr_headers)
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Project X"


def test_engineer_can_create_project(client, db_tables, lab, eng_headers):
    resp = client.post(f"/labs/{lab}/projects",
                       json={"name": "Eng Project"},
                       headers=eng_headers)
    assert resp.status_code == 403


def test_researcher_cannot_create_project(client, db_tables, lab, res_headers):
    resp = client.post(f"/labs/{lab}/projects",
                       json={"name": "Forbidden"},
                       headers=res_headers)
    assert resp.status_code == 403


# ── Get ───────────────────────────────────────────────────────────────────────

def test_get_project_returns_200(client, db_tables, lab, manager, mgr_headers):
    created = client.post(f"/labs/{lab}/projects",
                          json={"name": "P", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    resp = client.get(f"/labs/{lab}/projects/{created['id']}",
                      headers=mgr_headers)
    assert resp.status_code == 200


# ── Update ────────────────────────────────────────────────────────────────────

def test_engineer_can_update_project(client, db_tables, lab, manager,
                                      mgr_headers, eng_headers):
    created = client.post(f"/labs/{lab}/projects",
                          json={"name": "Old", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    resp = client.put(f"/labs/{lab}/projects/{created['id']}",
                      json={"name": "New", "status": "active"},
                      headers=eng_headers)
    assert resp.status_code == 403


# ── Delete ────────────────────────────────────────────────────────────────────

def test_manager_can_delete_project(client, db_tables, lab, manager, mgr_headers):
    created = client.post(f"/labs/{lab}/projects",
                          json={"name": "ToDelete", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    resp = client.delete(f"/labs/{lab}/projects/{created['id']}",
                         headers=mgr_headers)
    assert resp.status_code == 204


def test_engineer_cannot_delete_project(client, db_tables, lab, manager,
                                         mgr_headers, eng_headers):
    created = client.post(f"/labs/{lab}/projects",
                          json={"name": "Protected", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    resp = client.delete(f"/labs/{lab}/projects/{created['id']}",
                         headers=eng_headers)
    assert resp.status_code == 403


# ── Member association ────────────────────────────────────────────────────────

def test_add_member_to_project(client, db_tables, lab, manager, researcher, mgr_headers):
    project = client.post(f"/labs/{lab}/projects",
                          json={"name": "Team Proj", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    resp = client.post(f"/labs/{lab}/projects/{project['id']}/members",
                       json={"member_id": researcher},
                       headers=mgr_headers)
    assert resp.status_code == 200
    member_ids = [m["id"] for m in resp.get_json()["members"]]
    assert researcher in member_ids


def test_add_duplicate_member_to_project_returns_409(client, db_tables, lab,
                                                      manager, researcher, mgr_headers):
    project = client.post(f"/labs/{lab}/projects",
                          json={"name": "Dup Proj", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    client.post(f"/labs/{lab}/projects/{project['id']}/members",
                json={"member_id": researcher}, headers=mgr_headers)
    resp = client.post(f"/labs/{lab}/projects/{project['id']}/members",
                       json={"member_id": researcher}, headers=mgr_headers)
    assert resp.status_code == 409


def test_remove_member_from_project(client, db_tables, lab, manager, researcher,
                                     mgr_headers):
    project = client.post(f"/labs/{lab}/projects",
                          json={"name": "Rem Proj", "tech_lead_id": manager},
                          headers=mgr_headers).get_json()
    client.post(f"/labs/{lab}/projects/{project['id']}/members",
                json={"member_id": researcher}, headers=mgr_headers)
    resp = client.delete(
        f"/labs/{lab}/projects/{project['id']}/members/{researcher}",
        headers=mgr_headers,
    )
    assert resp.status_code == 204
