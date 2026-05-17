import marshmallow as msh

from labmm.extensions import ma
from labmm.models.lab_membership import CompensationType, LabMembership, LabRole


class LabMembershipSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LabMembership
        load_instance = True
        include_fk = True

    role = msh.fields.String()
    compensation_type = msh.fields.Enum(
        CompensationType, by_value=True, allow_none=True, dump_default=None
    )
    member = ma.Nested("MemberSchema", exclude=("lab_memberships",), dump_only=True)
    laboratory = ma.Nested("LaboratorySchema", dump_only=True)


class LabMembershipInputSchema(msh.Schema):
    member_id = msh.fields.Integer(required=True)
    role = msh.fields.String(required=True)
    specialization = msh.fields.String(load_default=None, allow_none=True)
    compensation_type = msh.fields.String(
        load_default=None,
        allow_none=True,
        validate=msh.validate.OneOf([c.value for c in CompensationType]),
    )
    compensation_value = msh.fields.Decimal(
        load_default=None, allow_none=True, places=2
    )


class LabMembershipUpdateSchema(msh.Schema):
    role = msh.fields.String(required=True)
    specialization = msh.fields.String(load_default=None, allow_none=True)
    compensation_type = msh.fields.String(
        load_default=None,
        allow_none=True,
        validate=msh.validate.OneOf([c.value for c in CompensationType]),
    )
    compensation_value = msh.fields.Decimal(
        load_default=None, allow_none=True, places=2
    )
    reports_to_id = msh.fields.Integer(load_default=None, allow_none=True)


lab_membership_schema = LabMembershipSchema()
lab_memberships_schema = LabMembershipSchema(many=True)
lab_membership_input_schema = LabMembershipInputSchema()
lab_membership_update_schema = LabMembershipUpdateSchema()
