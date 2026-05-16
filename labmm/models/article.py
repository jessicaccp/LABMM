from labmm.extensions import db

article_authors = db.Table(
    "article_authors",
    db.Column(
        "member_id",
        db.Integer,
        db.ForeignKey("members.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "article_id",
        db.Integer,
        db.ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=True)
    journal = db.Column(db.String(128), nullable=True)
    doi = db.Column(db.String(128), unique=True, nullable=True)
    published_at = db.Column(db.Date, nullable=True)
    lab_id = db.Column(
        db.Integer,
        db.ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    laboratory = db.relationship("Laboratory", back_populates="articles")
    authors = db.relationship(
        "Member", secondary="article_authors", back_populates="authored_articles"
    )

    def __repr__(self) -> str:
        return f"<Article {self.title}>"
