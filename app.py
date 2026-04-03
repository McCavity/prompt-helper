import os
import secrets
from datetime import timedelta

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, PromptBuilderForm, SignupForm
from models import Prompt, User, db
from translations import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, TRANSLATIONS


def assemble_prompt(expertise, task, context, constraints=None):
    parts = [
        f"You are a top 0.1% expert in {expertise}.",
        f"TASK: {task}",
        f"CONTEXT: {context}",
    ]
    if constraints and constraints.strip():
        parts.append(f"CONSTRAINTS: {constraints}")
    parts.append(
        "Ask me clarifying questions one at a time until you are at least "
        "95% confident that you can successfully finish the task."
    )
    return "\n\n".join(parts)


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///prompt_helper.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Extensions
    db.init_app(app)
    csrf = CSRFProtect(app)  # noqa: F841
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"
    login_manager.login_message = "flash_login_required"

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["30 per minute"],
        storage_uri="memory://",
    )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.context_processor
    def inject_i18n():
        lang = session.get("lang", DEFAULT_LANGUAGE)
        strings = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])

        def _(key, **kwargs):
            text = strings.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
            return text.format(**kwargs) if kwargs else text

        return {"_": _, "lang": lang, "SUPPORTED_LANGUAGES": SUPPORTED_LANGUAGES}

    # --- Routes ---

    @app.route("/set-language/<lang>")
    def set_language(lang):
        if lang in SUPPORTED_LANGUAGES:
            session["lang"] = lang
        return redirect(request.referrer or url_for("index"))

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("builder"))
        return redirect(url_for("login"))

    @app.route("/signup", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("builder"))
        form = SignupForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("flash_username_taken", "error")
                return render_template("signup.html", form=form)
            if User.query.filter_by(email=form.email.data).first():
                flash("flash_email_taken", "error")
                return render_template("signup.html", form=form)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("flash_account_created", "success")
            return redirect(url_for("builder"))
        return render_template("signup.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("builder"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("builder"))
            flash("flash_invalid_credentials", "error")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("flash_logged_out", "info")
        return redirect(url_for("login"))

    @app.route("/builder", methods=["GET", "POST"])
    @login_required
    def builder():
        form = PromptBuilderForm()
        if form.validate_on_submit():
            assembled = assemble_prompt(
                form.expertise.data,
                form.task.data,
                form.context.data,
                form.constraints.data,
            )
            prompt = Prompt(
                user_id=current_user.id,
                expertise=form.expertise.data,
                task=form.task.data,
                context=form.context.data,
                constraints=form.constraints.data,
                assembled=assembled,
            )
            db.session.add(prompt)
            db.session.commit()
            flash("flash_prompt_saved", "success")
            return redirect(url_for("prompt_detail", prompt_id=prompt.id))
        return render_template("builder.html", form=form)

    @app.route("/library")
    @login_required
    def library():
        search = request.args.get("q", "").strip()
        page = request.args.get("page", 1, type=int)
        query = Prompt.query.filter_by(user_id=current_user.id)
        if search:
            query = query.filter(Prompt.assembled.ilike(f"%{search}%"))
        pagination = query.order_by(Prompt.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template(
            "library.html", prompts=pagination.items, pagination=pagination, search=search
        )

    @app.route("/prompt/<int:prompt_id>")
    @login_required
    def prompt_detail(prompt_id):
        prompt = db.session.get(Prompt, prompt_id)
        if not prompt or prompt.user_id != current_user.id:
            abort(403)
        return render_template("prompt_detail.html", prompt=prompt)

    @app.route("/prompt/<int:prompt_id>/copy")
    @login_required
    def prompt_copy(prompt_id):
        prompt = db.session.get(Prompt, prompt_id)
        if not prompt or prompt.user_id != current_user.id:
            abort(403)
        form = PromptBuilderForm(
            expertise=prompt.expertise,
            task=prompt.task,
            context=prompt.context,
            constraints=prompt.constraints,
        )
        return render_template("builder.html", form=form)

    @app.route("/prompt/<int:prompt_id>/delete", methods=["POST"])
    @login_required
    def prompt_delete(prompt_id):
        prompt = db.session.get(Prompt, prompt_id)
        if not prompt or prompt.user_id != current_user.id:
            abort(403)
        db.session.delete(prompt)
        db.session.commit()
        flash("flash_prompt_deleted", "info")
        return redirect(url_for("library"))

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    debug = os.environ.get("FLASK_ENV") != "production"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
