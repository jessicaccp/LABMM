from flask import Blueprint, abort, jsonify, request
from marshmallow import ValidationError

from labmm.extensions import db
from labmm.models.article import Article, ArticleStatus
from labmm.models.lab_membership import LabRole
from labmm.models.laboratory import Laboratory
from labmm.schemas.article_schema import (
    article_input_schema,
    article_schema,
    articles_schema,
)
from labmm.utils.decorators import require_lab_role

bp = Blueprint("articles", __name__)


@bp.get("/labs/<int:lab_id>/articles")
def list_articles(lab_id: int):
    """Public endpoint — no token required.
    Pass ?published_only=true to return only published articles.
    """
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        abort(404, "Laboratory not found.")

    published_only = request.args.get("published_only", "").lower() in ("1", "true", "yes")
    query = Article.query.filter_by(lab_id=lab_id)
    if published_only:
        query = query.filter_by(status=ArticleStatus.published)

    return jsonify(articles_schema.dump(query.all())), 200


@bp.get("/labs/<int:lab_id>/articles/<int:article_id>")
def get_article(lab_id: int, article_id: int):
    """Public endpoint — no token required."""
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    return jsonify(article_schema.dump(article)), 200


@bp.post("/labs/<int:lab_id>/articles")
@require_lab_role(LabRole.ceo, LabRole.chief_scientist, LabRole.researcher, LabRole.research_fellow)
def create_article(lab_id: int):
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        abort(404, "Laboratory not found.")
    data = request.get_json(silent=True) or {}
    try:
        article = article_input_schema.load(data)
    except ValidationError as exc:
        return jsonify(errors=exc.messages), 422
    article.lab_id = lab_id
    db.session.add(article)
    db.session.commit()
    return jsonify(article_schema.dump(article)), 201


@bp.put("/labs/<int:lab_id>/articles/<int:article_id>")
@require_lab_role(LabRole.ceo, LabRole.chief_scientist, LabRole.researcher, LabRole.research_fellow)
def update_article(lab_id: int, article_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    data = request.get_json(silent=True) or {}
    try:
        article = article_input_schema.load(data, instance=article, partial=True)
    except ValidationError as exc:
        return jsonify(errors=exc.messages), 422
    db.session.commit()
    return jsonify(article_schema.dump(article)), 200


@bp.delete("/labs/<int:lab_id>/articles/<int:article_id>")
@require_lab_role(LabRole.ceo, LabRole.chief_scientist)
def delete_article(lab_id: int, article_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    db.session.delete(article)
    db.session.commit()
    return "", 204


@bp.post("/labs/<int:lab_id>/articles/<int:article_id>/deactivate")
@require_lab_role(LabRole.ceo, LabRole.chief_scientist)
def deactivate_article(lab_id: int, article_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    article.is_active = False
    db.session.commit()
    return jsonify(article_schema.dump(article)), 200


@bp.post("/labs/<int:lab_id>/articles/<int:article_id>/activate")
@require_lab_role(LabRole.ceo, LabRole.chief_scientist)
def activate_article(lab_id: int, article_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    article.is_active = True
    db.session.commit()
    return jsonify(article_schema.dump(article)), 200
