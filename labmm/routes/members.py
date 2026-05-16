from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from labmm.extensions import db
from labmm.models.lab_membership import LabMembership, LabRole
from labmm.models.laboratory import Laboratory
from labmm.models.member import Member
from labmm.schemas.lab_membership_schema import (
    lab_membership_input_schema,
    lab_membership_schema,
    lab_memberships_schema,
)
from labmm.schemas.member_schema import member_schema, members_schema
from labmm.utils.decorators import require_lab_member, require_lab_role

bp = Blueprint("members", __name__)


@bp.get("/labs/<int:lab_id>/members")
@require_lab_member
def list_members(lab_id: int):
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        abort(404, "Laboratory not found.")
    memberships = LabMembership.query.filter_by(lab_id=lab_id).all()
    return jsonify(lab_memberships_schema.dump(memberships)), 200


@bp.post("/labs/<int:lab_id>/members")
@require_lab_role(LabRole.manager)
def add_member(lab_id: int):
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        abort(404, "Laboratory not found.")

    data = request.get_json(silent=True) or {}
    try:
        payload = lab_membership_input_schema.load(data)
    except ValidationError as exc:
        return jsonify(errors=exc.messages), 422

    member = db.session.get(Member, payload["member_id"])
    if not member:
        abort(404, "Member not found.")

    existing = LabMembership.query.filter_by(
        member_id=member.id, lab_id=lab_id
    ).first()
    if existing:
        return jsonify(error="Member already belongs to this laboratory."), 409

    membership = LabMembership(
        member_id=member.id, lab_id=lab_id, role=LabRole(payload["role"])
    )
    db.session.add(membership)
    db.session.commit()
    return jsonify(lab_membership_schema.dump(membership)), 201


@bp.get("/labs/<int:lab_id>/members/<int:member_id>")
@require_lab_member
def get_member(lab_id: int, member_id: int):
    membership = LabMembership.query.filter_by(
        lab_id=lab_id, member_id=member_id
    ).first()
    if not membership:
        abort(404, "Member not found in this laboratory.")
    return jsonify(lab_membership_schema.dump(membership)), 200


@bp.put("/labs/<int:lab_id>/members/<int:member_id>")
@require_lab_role(LabRole.manager)
def update_member_role(lab_id: int, member_id: int):
    membership = LabMembership.query.filter_by(
        lab_id=lab_id, member_id=member_id
    ).first()
    if not membership:
        abort(404, "Member not found in this laboratory.")

    data = request.get_json(silent=True) or {}
    role_value = data.get("role")
    if not role_value:
        return jsonify(error="'role' field is required."), 422
    try:
        membership.role = LabRole(role_value)
    except ValueError:
        return jsonify(error=f"Invalid role '{role_value}'."), 422

    db.session.commit()
    return jsonify(lab_membership_schema.dump(membership)), 200


@bp.delete("/labs/<int:lab_id>/members/<int:member_id>")
@require_lab_role(LabRole.manager)
def remove_member(lab_id: int, member_id: int):
    membership = LabMembership.query.filter_by(
        lab_id=lab_id, member_id=member_id
    ).first()
    if not membership:
        abort(404, "Member not found in this laboratory.")
    db.session.delete(membership)
    db.session.commit()
    return "", 204


# --- Own profile update (any authenticated lab member or super-admin) ---

@bp.put("/members/<int:member_id>")
@jwt_required()
def update_own_profile(member_id: int):
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    identity = int(get_jwt_identity())

    # Members can only edit themselves; super-admins can edit anyone
    if identity != member_id and not claims.get("is_super_admin"):
        abort(403, "You can only update your own profile.")

    member = db.session.get(Member, member_id)
    if not member:
        abort(404, "Member not found.")

    data = request.get_json(silent=True) or {}
    allowed = ("first_name", "last_name")
    for field in allowed:
        if field in data:
            setattr(member, field, data[field])

    if "password" in data:
        member.set_password(data["password"])

    db.session.commit()
    return jsonify(member_schema.dump(member)), 200
