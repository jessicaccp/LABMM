import marshmallow as msh

from labmm.extensions import ma
from labmm.models.lab_membership import LabMembership, LabRole


class LabMembershipSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LabMembership
        load_instance = True
        include_fk = True

    role = msh.fields.Enum(LabRole, by_value=True)
    member = ma.Nested("MemberSchema", exclude=("lab_memberships",), dump_only=True)
    laboratory = ma.Nested("LaboratorySchema", dump_only=True)


class LabMembershipInputSchema(msh.Schema):
    member_id = msh.fields.Integer(required=True)
    role = msh.fields.String(
        required=True,
        validate=msh.validate.OneOf([r.value for r in LabRole]),
    )


lab_membership_schema = LabMembershipSchema()
lab_memberships_schema = LabMembershipSchema(many=True)
lab_membership_input_schema = LabMembershipInputSchema()
