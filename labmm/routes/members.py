from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from labmm.extensions import db
from labmm.models.lab_membership import CompensationType, LabMembership, LabRole, MANAGER_ROLES
from labmm.models.laboratory import Laboratory
from labmm.models.member import Member
from labmm.schemas.lab_membership_schema import (
    lab_membership_input_schema,
    lab_membership_schema,
    lab_membership_update_schema,
    lab_memberships_schema,
)
from labmm.schemas.member_schema import member_schema, members_schema
from labmm.utils.decorators import require_lab_member, require_lab_role

bp = Blueprint("members", __name__)


@bp.get("/members/<int:member_id>")
@jwt_required()
def get_member_detail(member_id: int):
    """Super-admin or CEO: return a single member with full lab_memberships."""
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    current_id = get_jwt_identity()

    if not claims.get("is_super_admin"):
        # CEOs may access members that belong to one of their labs
        ceo_lab_ids = [
            m.lab_id for m in LabMembership.query.filter_by(
                member_id=current_id, role=LabRole.ceo
            ).all()
        ]
        if not ceo_lab_ids:
            abort(403, "Super-admin or CEO access required.")
        in_lab = LabMembership.query.filter(
            LabMembership.member_id == member_id,
            LabMembership.lab_id.in_(ceo_lab_ids)
        ).first()
        if not in_lab:
            abort(403, "Access denied.")

    member = db.session.get(Member, member_id)
    if not member:
        abort(404, "Member not found.")
    return jsonify(member_schema.dump(member)), 200


@bp.get("/members")
@jwt_required()
def list_all_members():
    """Super-admin or CEO: list members (CEOs see only their labs' members)."""
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    current_id = get_jwt_identity()

    if claims.get("is_super_admin"):
        members = Member.query.order_by(Member.last_name, Member.first_name).all()
        return jsonify(members_schema.dump(members)), 200

    # Allow CEOs to list members of labs they lead
    ceo_lab_ids = [
        m.lab_id for m in LabMembership.query.filter_by(
            member_id=current_id, role=LabRole.ceo
        ).all()
    ]
    if not ceo_lab_ids:
        abort(403, "Access denied.")

    member_ids = [
        row[0] for row in db.session.query(LabMembership.member_id)
        .filter(LabMembership.lab_id.in_(ceo_lab_ids))
        .distinct()
        .all()
    ]
    members = Member.query.filter(Member.id.in_(member_ids)).order_by(
        Member.last_name, Member.first_name
    ).all()
    return jsonify(members_schema.dump(members)), 200


@bp.get("/labs/<int:lab_id>/members")
@require_lab_member
def list_members(lab_id: int):
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        abort(404, "Laboratory not found.")
    memberships = LabMembership.query.filter_by(lab_id=lab_id).all()
    return jsonify(lab_memberships_schema.dump(memberships)), 200


@bp.post("/labs/<int:lab_id>/members")
@require_lab_role(LabRole.ceo)
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

    ct = payload.get("compensation_type")
    membership = LabMembership(
        member_id=member.id,
        lab_id=lab_id,
        role=LabRole(payload["role"]),
        specialization=payload.get("specialization"),
        compensation_type=CompensationType(ct) if ct else None,
        compensation_value=payload.get("compensation_value"),
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
@require_lab_role(LabRole.ceo)
def update_member_role(lab_id: int, member_id: int):
    membership = LabMembership.query.filter_by(
        lab_id=lab_id, member_id=member_id
    ).first()
    if not membership:
        abort(404, "Member not found in this laboratory.")

    data = request.get_json(silent=True) or {}
    try:
        payload = lab_membership_update_schema.load(data)
    except ValidationError as exc:
        return jsonify(errors=exc.messages), 422

    membership.role = LabRole(payload["role"])
    if "specialization" in data:
        membership.specialization = payload.get("specialization")
    ct = payload.get("compensation_type")
    if "compensation_type" in data:
        membership.compensation_type = CompensationType(ct) if ct else None
    if "compensation_value" in data:
        membership.compensation_value = payload.get("compensation_value")

    db.session.commit()
    return jsonify(lab_membership_schema.dump(membership)), 200


@bp.delete("/labs/<int:lab_id>/members/<int:member_id>")
@require_lab_role(LabRole.ceo)
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

    # Super-admins can promote/demote professor status
    if claims.get("is_super_admin") and "is_professor" in data:
        member.is_professor = bool(data["is_professor"])

    if "password" in data:
        member.set_password(data["password"])

    db.session.commit()
    return jsonify(member_schema.dump(member)), 200


@bp.get("/members/lookup")
@jwt_required()
def lookup_member():
    """Look up a member by CPF. Returns basic member info (id, name, email)."""
    raw = request.args.get("cpf", "")
    cpf = raw.replace(".", "").replace("-", "").strip()
    if not cpf or not cpf.isdigit() or len(cpf) != 11:
        return jsonify(error="Invalid CPF."), 422
    member = Member.query.filter_by(cpf=cpf).first()
    if not member:
        abort(404, "No member found with this CPF.")
    return jsonify(member_schema.dump(member)), 200


@bp.get("/members/pending")
@jwt_required()
def list_pending_members():
    """Return all unapproved members. Professors see only their CEO labs' pending members."""
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get("is_super_admin"):
        pending = Member.query.filter_by(is_approved=False).all()
    elif claims.get("is_professor"):
        member_id = int(get_jwt_identity())
        ceo_lab_ids = [
            m.lab_id for m in LabMembership.query.filter_by(member_id=member_id, role=LabRole.ceo)
        ]
        pending = Member.query.filter(
            Member.is_approved == False,  # noqa: E712
            Member.desired_lab_id.in_(ceo_lab_ids),
        ).all()
    else:
        abort(403, "Professor or super-admin access required.")
    return jsonify(members_schema.dump(pending)), 200


@bp.post("/members/<int:member_id>/approve")
@jwt_required()
def approve_member(member_id: int):
    """Approve a pending member. Professors may only approve members for their CEO labs."""
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    is_super_admin = claims.get("is_super_admin")
    is_professor = claims.get("is_professor")
    if not (is_super_admin or is_professor):
        abort(403, "Professor or super-admin access required.")

    member = db.session.get(Member, member_id)
    if not member:
        abort(404, "Member not found.")
    if member.is_approved:
        return jsonify(member_schema.dump(member)), 200

    if not is_super_admin:
        # Professors may only approve members assigned to their CEO labs
        caller_id = int(get_jwt_identity())
        ceo_lab_ids = [
            m.lab_id for m in LabMembership.query.filter_by(member_id=caller_id, role=LabRole.ceo)
        ]
        if member.desired_lab_id not in ceo_lab_ids:
            abort(403, "You can only approve members who requested access to your laboratory.")

    member.is_approved = True
    member.desired_lab_id = None
    db.session.commit()
    return jsonify(member_schema.dump(member)), 200


@bp.post("/members/<int:member_id>/deactivate")
@jwt_required()
def deactivate_member(member_id: int):
    """Super-admin: deactivate a member account (blocks login)."""
    from flask_jwt_extended import get_jwt
    if not get_jwt().get("is_super_admin"):
        abort(403, "Super-admin access required.")
    member = db.session.get(Member, member_id)
    if not member:
        abort(404, "Member not found.")
    if member.is_super_admin:
        abort(400, "Cannot deactivate a super-admin account.")
    member.is_active = False
    db.session.commit()
    return jsonify(member_schema.dump(member)), 200


@bp.post("/members/<int:member_id>/activate")
@jwt_required()
def activate_member(member_id: int):
    """Super-admin: reactivate a previously deactivated member."""
    from flask_jwt_extended import get_jwt
    if not get_jwt().get("is_super_admin"):
        abort(403, "Super-admin access required.")
    member = db.session.get(Member, member_id)
    if not member:
        abort(404, "Member not found.")
    member.is_active = True
    db.session.commit()
    return jsonify(member_schema.dump(member)), 200
