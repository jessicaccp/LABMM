import pytest
from flask_jwt_extended import create_access_token

from labmm import create_app
from labmm.extensions import db as _db
from labmm.models.lab_membership import LabMembership, LabRole
from labmm.models.laboratory import Laboratory
from labmm.models.member import Member


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def db_tables(app):
    """Create all tables before each test and drop them after."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_member(app, first="Test", last="User", email="test@lab.local",
                 password="password123", is_super_admin=False):
    with app.app_context():
        m = Member(first_name=first, last_name=last, email=email,
                   is_super_admin=is_super_admin)
        m.set_password(password)
        _db.session.add(m)
        _db.session.commit()
        return m.id


def _token_headers(app, member_id):
    with app.app_context():
        member = _db.session.get(Member, member_id)
        token = create_access_token(
            identity=str(member.id),
            additional_claims={"is_super_admin": member.is_super_admin},
        )
        return {"Authorization": f"Bearer {token}"}


# ── global fixtures ───────────────────────────────────────────────────────────

@pytest.fixture()
def super_admin(app, db_tables):
    mid = _make_member(app, first="Admin", last="Super",
                       email="admin@lab.local", is_super_admin=True)
    return mid


@pytest.fixture()
def sa_headers(app, super_admin):
    return _token_headers(app, super_admin)


@pytest.fixture()
def lab(app, db_tables, super_admin):
    with app.app_context():
        laboratory = Laboratory(name="Test Lab", description="A test laboratory")
        _db.session.add(laboratory)
        _db.session.commit()
        return laboratory.id


@pytest.fixture()
def manager(app, db_tables, lab):
    mid = _make_member(app, first="Lab", last="Manager",
                       email="manager@lab.local")
    with app.app_context():
        membership = LabMembership(member_id=mid, lab_id=lab,
                                   role=LabRole.manager)
        _db.session.add(membership)
        _db.session.commit()
    return mid


@pytest.fixture()
def engineer(app, db_tables, lab):
    mid = _make_member(app, first="Lab", last="Engineer",
                       email="engineer@lab.local")
    with app.app_context():
        membership = LabMembership(member_id=mid, lab_id=lab,
                                   role=LabRole.engineer)
        _db.session.add(membership)
        _db.session.commit()
    return mid


@pytest.fixture()
def researcher(app, db_tables, lab):
    mid = _make_member(app, first="Lab", last="Researcher",
                       email="researcher@lab.local")
    with app.app_context():
        membership = LabMembership(member_id=mid, lab_id=lab,
                                   role=LabRole.researcher)
        _db.session.add(membership)
        _db.session.commit()
    return mid


@pytest.fixture()
def staff(app, db_tables, lab):
    mid = _make_member(app, first="Lab", last="Staff",
                       email="staff@lab.local")
    with app.app_context():
        membership = LabMembership(member_id=mid, lab_id=lab,
                                   role=LabRole.staff)
        _db.session.add(membership)
        _db.session.commit()
    return mid


@pytest.fixture()
def mgr_headers(app, manager):
    return _token_headers(app, manager)


@pytest.fixture()
def eng_headers(app, engineer):
    return _token_headers(app, engineer)


@pytest.fixture()
def res_headers(app, researcher):
    return _token_headers(app, researcher)


@pytest.fixture()
def stf_headers(app, staff):
    return _token_headers(app, staff)
