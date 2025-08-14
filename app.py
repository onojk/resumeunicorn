import os
from flask import Flask, render_template, abort
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import RequestEntityTooLarge
from flask import request
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from forms import ResumeRequestForm
from utils import clean_text

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-me"),
    MAX_CONTENT_LENGTH=256 * 1024,   # 256 KB
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_TIME_LIMIT=None,
)

CSRFProtect(app)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["20/minute", "200/hour"], storage_uri=os.environ.get("LIMITER_STORAGE_URI", "redis://127.0.0.1:6379/0"))

@app.route("/", methods=["GET", "POST"])
@limiter.limit("5/minute; 40/hour")
def index():
    form = ResumeRequestForm()
    if form.validate_on_submit():
        # basic honeypot: bots fill this hidden field; humans do not

        if request.form.get("hp"):

            abort(400, description="Invalid input.")



        linkedin = clean_text(form.linkedin.data or "", 200)

        years    = form.years.data if form.years.data is not None else ""

        skills   = clean_text(form.skills.data or "", 200)

        name    = clean_text(form.name.data,    80)
        email   = clean_text(form.email.data,   120)
        role    = clean_text(form.role.data,    100)
        summary = clean_text(form.summary.data, 500)

        if not name or not role or "@" not in email:
            abort(400, description="Invalid input.")

        # TODO: your generation logic here
        return render_template("success.html", name=name)

    return render_template("form.html", form=form), (400 if form.errors else 200)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=False)

from flask import jsonify
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import RequestEntityTooLarge

@limiter.exempt

# --- healthz (clean single definition) ---
@limiter.exempt
@app.route("/healthz", endpoint="healthz")
def healthcheck():
    return jsonify(status="ok"), 200
# --- end healthz ---

@app.errorhandler(RequestEntityTooLarge)

def handle_413(e):

    return "Request too large", 413


@app.errorhandler(CSRFError)
def handle_csrf(e):
    ct = (request.mimetype or "")
    if request.method == "POST" and ct.startswith("application/json"):
        return "Unsupported Media Type", 415
    return (getattr(e, "description", "Bad Request")), 400
