# ── Public GET (no token required) ───────────────────────────────────────────

def test_list_articles_is_public(client, db_tables, lab):
    resp = client.get(f"/labs/{lab}/articles")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_article_is_public(client, db_tables, lab, mgr_headers):
    created = client.post(f"/labs/{lab}/articles",
                          json={"title": "Public Paper"},
                          headers=mgr_headers).get_json()
    resp = client.get(f"/labs/{lab}/articles/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Public Paper"


def test_get_nonexistent_article_returns_404(client, db_tables, lab):
    resp = client.get(f"/labs/{lab}/articles/9999")
    assert resp.status_code == 404


# ── Create ────────────────────────────────────────────────────────────────────

def test_researcher_can_create_article(client, db_tables, lab, res_headers):
    resp = client.post(f"/labs/{lab}/articles",
                       json={"title": "Researcher Paper", "journal": "Nature"},
                       headers=res_headers)
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Researcher Paper"


def test_engineer_can_create_article(client, db_tables, lab, eng_headers):
    resp = client.post(f"/labs/{lab}/articles",
                       json={"title": "Eng Paper"},
                       headers=eng_headers)
    assert resp.status_code == 201


def test_staff_cannot_create_article(client, db_tables, lab, stf_headers):
    resp = client.post(f"/labs/{lab}/articles",
                       json={"title": "Staff Paper"},
                       headers=stf_headers)
    assert resp.status_code == 403


def test_create_article_without_token_returns_401(client, db_tables, lab):
    resp = client.post(f"/labs/{lab}/articles",
                       json={"title": "Anon Paper"})
    assert resp.status_code == 401


# ── Update ────────────────────────────────────────────────────────────────────

def test_researcher_can_update_article(client, db_tables, lab, res_headers):
    created = client.post(f"/labs/{lab}/articles",
                          json={"title": "Draft"},
                          headers=res_headers).get_json()
    resp = client.put(f"/labs/{lab}/articles/{created['id']}",
                      json={"title": "Final"},
                      headers=res_headers)
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Final"


# ── Delete ────────────────────────────────────────────────────────────────────

def test_manager_can_delete_article(client, db_tables, lab, mgr_headers):
    created = client.post(f"/labs/{lab}/articles",
                          json={"title": "ToDelete"},
                          headers=mgr_headers).get_json()
    resp = client.delete(f"/labs/{lab}/articles/{created['id']}",
                         headers=mgr_headers)
    assert resp.status_code == 204


def test_researcher_cannot_delete_article(client, db_tables, lab, res_headers,
                                           mgr_headers):
    created = client.post(f"/labs/{lab}/articles",
                          json={"title": "Protected"},
                          headers=mgr_headers).get_json()
    resp = client.delete(f"/labs/{lab}/articles/{created['id']}",
                         headers=res_headers)
    assert resp.status_code == 403


# ── Authors ───────────────────────────────────────────────────────────────────

def test_add_author_to_article(client, db_tables, lab, researcher, mgr_headers):
    article = client.post(f"/labs/{lab}/articles",
                          json={"title": "Collab Paper"},
                          headers=mgr_headers).get_json()
    resp = client.post(f"/labs/{lab}/articles/{article['id']}/authors",
                       json={"member_id": researcher},
                       headers=mgr_headers)
    assert resp.status_code == 200
    author_ids = [a["id"] for a in resp.get_json()["authors"]]
    assert researcher in author_ids


def test_add_duplicate_author_returns_409(client, db_tables, lab, researcher,
                                           mgr_headers):
    article = client.post(f"/labs/{lab}/articles",
                          json={"title": "Dup Author"},
                          headers=mgr_headers).get_json()
    client.post(f"/labs/{lab}/articles/{article['id']}/authors",
                json={"member_id": researcher}, headers=mgr_headers)
    resp = client.post(f"/labs/{lab}/articles/{article['id']}/authors",
                       json={"member_id": researcher}, headers=mgr_headers)
    assert resp.status_code == 409


def test_remove_author_from_article(client, db_tables, lab, researcher,
                                     mgr_headers):
    article = client.post(f"/labs/{lab}/articles",
                          json={"title": "Remove Author"},
                          headers=mgr_headers).get_json()
    client.post(f"/labs/{lab}/articles/{article['id']}/authors",
                json={"member_id": researcher}, headers=mgr_headers)
    resp = client.delete(
        f"/labs/{lab}/articles/{article['id']}/authors/{researcher}",
        headers=mgr_headers,
    )
    assert resp.status_code == 204
