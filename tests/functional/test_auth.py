import json


# ── Bootstrap / Register ─────────────────────────────────────────────────────

def test_first_register_creates_super_admin(client, db_tables):
    resp = client.post("/auth/register", json={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@test.local",
        "password": "password123",
        "cpf": "00000000001",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["member"]["is_super_admin"] is True
    assert data["member"]["is_approved"] is True
    assert "access_token" in data


def test_second_register_without_token_creates_pending(client, db_tables):
    # Bootstrap first user
    client.post("/auth/register", json={
        "first_name": "Admin", "last_name": "User",
        "email": "admin@test.local", "password": "password123",
        "cpf": "00000000001",
    })
    # Self-registration without token — creates pending account, no tokens returned
    resp = client.post("/auth/register", json={
        "first_name": "Bob", "last_name": "Smith",
        "email": "bob@test.local", "password": "password123",
        "cpf": "00000000002",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["member"]["is_approved"] is False
    assert "access_token" not in data


def test_second_register_by_super_admin_succeeds(client, db_tables):
    r1 = client.post("/auth/register", json={
        "first_name": "Admin", "last_name": "User",
        "email": "admin@test.local", "password": "password123",
        "cpf": "00000000001",
    })
    token = r1.get_json()["access_token"]
    resp = client.post("/auth/register",
                       json={"first_name": "Bob", "last_name": "Smith",
                             "email": "bob@test.local", "password": "pass123",
                             "cpf": "00000000002"},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["member"]["is_super_admin"] is False
    assert data["member"]["is_approved"] is True
    assert "access_token" in data


def test_register_duplicate_email_returns_409(client, db_tables):
    payload = {"first_name": "A", "last_name": "B",
               "email": "dup@test.local", "password": "pass",
               "cpf": "00000000001"}
    client.post("/auth/register", json=payload)
    r1 = client.post("/auth/login",
                     json={"email": "dup@test.local", "password": "pass"})
    token = r1.get_json()["access_token"]
    resp = client.post("/auth/register", json={**payload, "cpf": "00000000002"},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 409


# ── Login ────────────────────────────────────────────────────────────────────

def test_login_valid_returns_tokens(client, db_tables):
    client.post("/auth/register", json={
        "first_name": "A", "last_name": "B",
        "email": "user@test.local", "password": "mypassword",
        "cpf": "00000000001",
    })
    resp = client.post("/auth/login",
                       json={"email": "user@test.local", "password": "mypassword"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password_returns_401(client, db_tables):
    client.post("/auth/register", json={
        "first_name": "A", "last_name": "B",
        "email": "user2@test.local", "password": "correct",
        "cpf": "00000000001",
    })
    resp = client.post("/auth/login",
                       json={"email": "user2@test.local", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email_returns_401(client, db_tables):
    resp = client.post("/auth/login",
                       json={"email": "ghost@test.local", "password": "x"})
    assert resp.status_code == 401


def test_pending_member_cannot_login(client, db_tables):
    # Bootstrap admin
    client.post("/auth/register", json={
        "first_name": "Admin", "last_name": "User",
        "email": "admin@test.local", "password": "password123",
        "cpf": "00000000001",
    })
    # Self-registration → pending
    client.post("/auth/register", json={
        "first_name": "Bob", "last_name": "Smith",
        "email": "bob@test.local", "password": "password123",
        "cpf": "00000000002",
    })
    resp = client.post("/auth/login",
                       json={"email": "bob@test.local", "password": "password123"})
    assert resp.status_code == 403


# ── Refresh ──────────────────────────────────────────────────────────────────

def test_refresh_returns_new_access_token(client, db_tables):
    client.post("/auth/register", json={
        "first_name": "A", "last_name": "B",
        "email": "ref@test.local", "password": "pass",
        "cpf": "00000000001",
    })
    login = client.post("/auth/login",
                        json={"email": "ref@test.local", "password": "pass"})
    refresh_token = login.get_json()["refresh_token"]
    resp = client.post("/auth/refresh",
                       headers={"Authorization": f"Bearer {refresh_token}"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


# ── /auth/me ─────────────────────────────────────────────────────────────────

def test_me_returns_current_user(client, db_tables, super_admin, sa_headers):
    resp = client.get("/auth/me", headers=sa_headers)
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "admin@lab.local"


def test_me_without_token_returns_401(client, db_tables):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
