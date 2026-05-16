from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from labmm.extensions import db
from labmm.models.member import Member
from labmm.schemas.member_schema import member_input_schema, member_schema

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _make_tokens(member: Member) -> dict:
    additional_claims = {"is_super_admin": member.is_super_admin}
    access_token = create_access_token(
        identity=str(member.id), additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=str(member.id), additional_claims=additional_claims
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@bp.post("/register")
def register():
    """
    Open only when no members exist (bootstrap).
    After the first member is created, only super-admins may register new members.
    """
    is_bootstrap = Member.query.count() == 0

    if not is_bootstrap:
        # Require super-admin JWT for subsequent registrations
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("is_super_admin"):
            abort(403, "Only super-admins can register new members.")

    data = request.get_json(silent=True) or {}

    # Normalize email so login (which also lowercases) can always find the account
    if "email" in data:
        data = {**data, "email": data["email"].strip().lower()}

    try:
        member = member_input_schema.load(data)
    except ValidationError as exc:
        return jsonify(errors=exc.messages), 422

    if Member.query.filter_by(email=member.email).first():
        return jsonify(error="Email already registered."), 409

    password = data.get("password", "")
    if len(password) < 8:
        return jsonify(errors={"password": ["Password must be at least 8 characters."]}), 422

    member.set_password(password)
    if is_bootstrap:
        member.is_super_admin = True

    db.session.add(member)
    db.session.commit()

    tokens = _make_tokens(member)
    return jsonify(member=member_schema.dump(member), **tokens), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    member = Member.query.filter_by(email=email).first()
    if not member or not member.check_password(password):
        abort(401, "Invalid email or password.")

    return jsonify(_make_tokens(member)), 200


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    member = db.session.get(Member, int(identity))
    if not member:
        abort(401, "Member not found.")
    additional_claims = {"is_super_admin": member.is_super_admin}
    access_token = create_access_token(
        identity=identity, additional_claims=additional_claims
    )
    return jsonify(access_token=access_token), 200


@bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    member = db.session.get(Member, int(identity))
    if not member:
        abort(401, "Member not found.")
    return jsonify(member_schema.dump(member)), 200
