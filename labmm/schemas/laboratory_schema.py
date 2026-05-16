from labmm.extensions import ma
from labmm.models.laboratory import Laboratory


class LaboratorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Laboratory
        load_instance = True


laboratory_schema = LaboratorySchema()
laboratories_schema = LaboratorySchema(many=True)
