import uuid

from flask import render_template
from flask_login import current_user

from app import db
from app.errors import bp
from app.main.forms import FavoriteActorForm, FavoriteMovieForm


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(ValueError)
def token_error_actor(error):
    if error.__str__() == "actor":
        form = FavoriteActorForm()
        token = str(uuid.uuid1())
        form.token.data = token
        current_user.token = token
        db.session.commit()
        return render_template("main/favorite_actor.html", title="Favorite Actor", form=form), 501
    else:
        form = FavoriteMovieForm()
        token = str(uuid.uuid1())
        form.token.data = token
        current_user.token = token
        db.session.commit()
        return render_template("main/favorite_movie.html", title="Favorite Movie", form=form), 501
