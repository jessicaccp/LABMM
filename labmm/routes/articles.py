from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from labmm.extensions import db
from labmm.models.article import Article
from labmm.models.lab_membership import LabRole
from labmm.models.laboratory import Laboratory
from labmm.models.member import Member
from labmm.schemas.article_schema import (
    article_input_schema,
    article_schema,
    articles_schema,
)
from labmm.utils.decorators import require_lab_role

bp = Blueprint("articles", __name__)


@bp.get("/labs/<int:lab_id>/articles")
def list_articles(lab_id: int):
    """Public endpoint — no token required."""
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        abort(404, "Laboratory not found.")
    return jsonify(articles_schema.dump(lab.articles)), 200


@bp.get("/labs/<int:lab_id>/articles/<int:article_id>")
def get_article(lab_id: int, article_id: int):
    """Public endpoint — no token required."""
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    return jsonify(article_schema.dump(article)), 200


@bp.post("/labs/<int:lab_id>/articles")
@require_lab_role(LabRole.manager, LabRole.engineer, LabRole.researcher)
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
@require_lab_role(LabRole.manager, LabRole.engineer, LabRole.researcher)
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
@require_lab_role(LabRole.manager)
def delete_article(lab_id: int, article_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    db.session.delete(article)
    db.session.commit()
    return "", 204


@bp.post("/labs/<int:lab_id>/articles/<int:article_id>/authors")
@require_lab_role(LabRole.manager, LabRole.engineer)
def add_author(lab_id: int, article_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    data = request.get_json(silent=True) or {}
    member_id = data.get("member_id")
    if not member_id:
        return jsonify(error="'member_id' is required."), 422
    member = db.session.get(Member, member_id)
    if not member:
        abort(404, "Member not found.")
    if member in article.authors:
        return jsonify(error="Member already an author of this article."), 409
    article.authors.append(member)
    db.session.commit()
    return jsonify(article_schema.dump(article)), 200


@bp.delete("/labs/<int:lab_id>/articles/<int:article_id>/authors/<int:member_id>")
@require_lab_role(LabRole.manager, LabRole.engineer)
def remove_author(lab_id: int, article_id: int, member_id: int):
    article = Article.query.filter_by(id=article_id, lab_id=lab_id).first()
    if not article:
        abort(404, "Article not found.")
    member = db.session.get(Member, member_id)
    if not member or member not in article.authors:
        abort(404, "Author not found on this article.")
    article.authors.remove(member)
    db.session.commit()
    return "", 204
