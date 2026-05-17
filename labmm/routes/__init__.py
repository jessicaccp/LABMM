from flask import Flask

from labmm.routes.articles import bp as articles_bp
from labmm.routes.auth import bp as auth_bp
from labmm.routes.laboratories import bp as labs_bp
from labmm.routes.members import bp as members_bp
from labmm.routes.projects import bp as projects_bp
from labmm.routes.research import bp as research_bp
from labmm.routes.roles import bp as roles_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(labs_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(research_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(roles_bp)

    if app.debug:
        from labmm.routes.debug import bp as debug_bp
        app.register_blueprint(debug_bp)
