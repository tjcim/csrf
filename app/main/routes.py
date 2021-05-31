import uuid
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app, g, \
    send_from_directory
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.models import User, Post
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, \
    FavoriteMovieForm, FavoriteActorForm


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/uploads/<path:name>')
@login_required
def download_file(name):
    return send_from_directory(current_app.config['STATIC_PATH'], name, as_attachment=True)


@bp.route('/favorite-actor/', methods=['GET', 'POST'])
@login_required
def favorite_actor():
    form = FavoriteActorForm()
    if request.method == "GET":
        token = str(uuid.uuid1())
        form.token.data = token
        current_user.token = token
        db.session.commit()
    if form.validate_on_submit():
        success = False
        if not form.token.data == current_user.token:
            flash("Token Error", "danger")
            raise ValueError("actor")
        if form.actor_name.data == "Nicolas Cage":
            flash("You got it!", "success")
            success = True
        else:
            flash("Nope. Try again.", "danger")
        token = str(uuid.uuid1())
        form.token.data = token
        current_user.token = token
        db.session.commit()
        return render_template("main/favorite_actor.html", title="Favorite Actor",
                               form=form, success=success)
    return render_template("main/favorite_actor.html", title="Favorite Actor", form=form)


@bp.route('/favorite-movie/', methods=['GET', 'POST'])
@login_required
def favorite_movie():
    form = FavoriteMovieForm()
    if request.method == "GET":
        token = str(uuid.uuid1())
        form.token.data = token
        current_user.token = token
        db.session.commit()
    if form.validate_on_submit():
        success = False
        if not form.token.data == current_user.token:
            flash("Token Error", "danger")
            raise ValueError()
        if form.movie_title.data == "Con Air":
            flash("You got it!", "success")
            success = True
        else:
            flash("Nope. Try again.", "danger")
        token = str(uuid.uuid1())
        form.token.data = token
        current_user.token = token
        db.session.commit()
        return render_template("main/favorite_movie.html", title="Favorite Movie",
                               form=form, success=success)
    return render_template("main/favorite_movie.html", title="Favorite Movie", form=form)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = url_for("main.index", page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for("main.index", page=posts.prev_num) \
        if posts.has_prev else None
    return render_template(
        'main/index.html', title='Home', form=form, posts=posts.items, next_url=next_url,
        prev_url=prev_url
    )


@bp.route("/explore/")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = url_for("main.explore", page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for("main.explore", page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('main/index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for("main.user", username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for("main.explore", username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('main/user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>/', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f"You are following {username}")
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.index"))


@bp.route('/unfollow/<username>/', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("main.index"))
        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("main.user", username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You are not following {username}.")
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.index"))


@bp.route('/search/')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('main/search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)
