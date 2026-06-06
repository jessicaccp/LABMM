from marshmallow import fields, validate

from labmm.extensions import ma
from labmm.models.article import Article, ArticleStatus


VALID_STATUSES = [s.value for s in ArticleStatus]


class ArticleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Article
        load_instance = True
        include_fk = True

    authors = ma.Nested("MemberSchema", many=True, only=("id", "first_name", "last_name"), dump_only=True)


class ArticleInputSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Article
        load_instance = True

    title = ma.auto_field(required=True)
    abstract = ma.auto_field()
    conference = ma.auto_field()
    doi = ma.auto_field()
    status = ma.auto_field(
        validate=validate.OneOf(VALID_STATUSES),
        load_default=ArticleStatus.in_progress.value,
        required=False,
    )
    submission_deadline = ma.auto_field()
    published_at = ma.auto_field()
    authors = ma.auto_field(load_default=list, required=False)
    in_charge = ma.auto_field(load_default=list, required=False)


article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
article_input_schema = ArticleInputSchema()
