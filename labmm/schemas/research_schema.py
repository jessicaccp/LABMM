from labmm.extensions import ma
from labmm.models.research import Research


class ResearchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Research
        load_instance = True
        include_fk = True

    members = ma.Nested(
        "MemberSchema", many=True, exclude=("lab_memberships",), dump_only=True
    )
    projects = ma.Nested("ProjectSchema", many=True, exclude=("members",), dump_only=True)


class ResearchInputSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Research
        load_instance = True

    name = ma.auto_field(required=True)
    description = ma.auto_field()


research_schema = ResearchSchema()
researches_schema = ResearchSchema(many=True, exclude=("members", "projects"))
research_input_schema = ResearchInputSchema()
