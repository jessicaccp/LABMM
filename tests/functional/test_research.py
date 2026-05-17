# ── List ─────────────────────────────────────────────────────────────────────

def test_any_member_can_list_research(client, db_tables, lab, stf_headers):
    resp = client.get(f"/labs/{lab}/research", headers=stf_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_list_research_without_token_returns_401(client, db_tables, lab):
    resp = client.get(f"/labs/{lab}/research")
    assert resp.status_code == 401


# ── Create ────────────────────────────────────────────────────────────────────

def test_manager_can_create_research(client, db_tables, lab, cs_headers):
    resp = client.post(f"/labs/{lab}/research",
                       json={"name": "AI Research", "description": "Desc"},
                       headers=cs_headers)
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "AI Research"


def test_engineer_cannot_create_research(client, db_tables, lab, eng_headers):
    resp = client.post(f"/labs/{lab}/research",
                       json={"name": "Rogue Group"},
                       headers=eng_headers)
    assert resp.status_code == 403


# ── Get ───────────────────────────────────────────────────────────────────────

def test_get_research_returns_200(client, db_tables, lab, cs_headers):
    created = client.post(f"/labs/{lab}/research",
                          json={"name": "Grp"},
                          headers=cs_headers).get_json()
    resp = client.get(f"/labs/{lab}/research/{created['id']}",
                      headers=cs_headers)
    assert resp.status_code == 200


# ── Update ────────────────────────────────────────────────────────────────────

def test_manager_can_update_research(client, db_tables, lab, cs_headers):
    created = client.post(f"/labs/{lab}/research",
                          json={"name": "Old"},
                          headers=cs_headers).get_json()
    resp = client.put(f"/labs/{lab}/research/{created['id']}",
                      json={"name": "New"},
                      headers=cs_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "New"


# ── Delete ────────────────────────────────────────────────────────────────────

def test_manager_can_delete_research(client, db_tables, lab, cs_headers):
    created = client.post(f"/labs/{lab}/research",
                          json={"name": "ToDelete"},
                          headers=cs_headers).get_json()
    resp = client.delete(f"/labs/{lab}/research/{created['id']}",
                         headers=cs_headers)
    assert resp.status_code == 204


# ── Member association ────────────────────────────────────────────────────────

def test_add_member_to_research(client, db_tables, lab, researcher,
                                 cs_headers):
    group = client.post(f"/labs/{lab}/research",
                        json={"name": "Grp"},
                        headers=cs_headers).get_json()
    resp = client.post(f"/labs/{lab}/research/{group['id']}/members",
                       json={"member_id": researcher},
                       headers=cs_headers)
    assert resp.status_code == 200
    member_ids = [m["id"] for m in resp.get_json()["members"]]
    assert researcher in member_ids


def test_add_duplicate_member_to_research_returns_409(client, db_tables, lab,
                                                        researcher, cs_headers):
    group = client.post(f"/labs/{lab}/research",
                        json={"name": "Grp2"},
                        headers=cs_headers).get_json()
    client.post(f"/labs/{lab}/research/{group['id']}/members",
                json={"member_id": researcher}, headers=cs_headers)
    resp = client.post(f"/labs/{lab}/research/{group['id']}/members",
                       json={"member_id": researcher},
                       headers=cs_headers)
    assert resp.status_code == 409


def test_remove_member_from_research(client, db_tables, lab, researcher,
                                      cs_headers):
    group = client.post(f"/labs/{lab}/research",
                        json={"name": "Grp3"},
                        headers=cs_headers).get_json()
    client.post(f"/labs/{lab}/research/{group['id']}/members",
                json={"member_id": researcher}, headers=cs_headers)
    resp = client.delete(
        f"/labs/{lab}/research/{group['id']}/members/{researcher}",
        headers=cs_headers,
    )
    assert resp.status_code == 204
