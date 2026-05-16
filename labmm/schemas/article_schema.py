from labmm.extensions import ma
from labmm.models.article import Article


class ArticleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Article
        load_instance = True
        include_fk = True

    authors = ma.Nested(
        "MemberSchema", many=True, exclude=("lab_memberships",), dump_only=True
    )


class ArticleInputSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Article
        load_instance = True

    title = ma.auto_field(required=True)
    abstract = ma.auto_field()
    journal = ma.auto_field()
    doi = ma.auto_field()
    published_at = ma.auto_field()


article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True, exclude=("authors",))
article_input_schema = ArticleInputSchema()
