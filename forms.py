from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp, URL, NumberRange, ValidationError
from urllib.parse import urlparse
import re

# --- regexes (not too strict; friendly but useful) ---
NAME_RE     = r"^[A-Za-z][A-Za-z\s\.'-]{1,79}$"
ROLE_RE     = r"^[A-Za-z0-9\s\-\&\(\)\/\.,]{2,100}$"
LOCATION_RE = r"^[A-Za-z0-9\s,\.\-'/]{2,120}$"
PHONE_RE    = r"^[0-9\+\-\s\(\)]{7,20}$"  # digits + () + - + spaces

def must_be_domain(*hosts):
    """Require URL host to be one of the supplied domains (or subdomains)."""
    allowed = tuple(h.lower() for h in hosts)
    def _check(form, field):
        if not field.data:
            return
        u = urlparse(field.data)
        host = (u.hostname or "").lower()
        if not any(host == d or host.endswith("." + d) for d in allowed):
            raise ValidationError(f"URL must be on {' or '.join(allowed)}")
    return _check

def clean_commalist(s: str, limit=200, max_items=20):
    """Normalize 'a, b , c' → 'a, b, c', allow tech punctuation, de-dup, cap length/items."""
    s = (s or "").strip()
    if not s:
        return ""
    parts = [p.strip() for p in s.split(",")]
    parts = [re.sub(r"[^A-Za-z0-9 +#\.\-]", "", p) for p in parts if p]
    out, seen = [], set()
    for p in parts:
        if p and p not in seen:
            out.append(p); seen.add(p)
        if len(out) >= max_items:
            break
    return (", ".join(out))[:limit]

class ResumeRequestForm(FlaskForm):
    # --- existing core fields ---
    name = StringField("Name",
        validators=[DataRequired(), Length(min=2, max=80),
                    Regexp(NAME_RE, message="Use letters, spaces, .'- only")])
    email = StringField("Email",
        validators=[DataRequired(), Email(), Length(max=120)])
    role = StringField("Target Role",
        validators=[DataRequired(), Length(min=2, max=100), Regexp(ROLE_RE)])
    summary = TextAreaField("Professional Summary",
        validators=[Optional(), Length(max=500)])
    linkedin = StringField("LinkedIn URL",
        validators=[Optional(), URL(require_tld=True, message="Use a full https:// URL"),
                    Length(max=200), must_be_domain("linkedin.com", "linkedin.cn")])
    years = IntegerField("Years of Experience",
        validators=[Optional(), NumberRange(min=0, max=60, message="0–60 only")])
    skills = StringField("Top Skills (comma-separated)",
        validators=[Optional(), Length(max=200)],
        filters=[lambda s: clean_commalist(s, 200, 20)])

    # --- new: contact / location ---
    phone = StringField("Phone",
        validators=[Optional(), Regexp(PHONE_RE, message="Use digits, +, -, spaces, () only (7–20 chars)")])
    location = StringField("Location (City, State/Region, Country)",
        validators=[Optional(), Length(min=2, max=120), Regexp(LOCATION_RE)])

    # --- new: job preferences ---
    work_mode = SelectField("Preferred Work Mode",
        choices=[("", "— select —"), ("remote","Remote"), ("hybrid","Hybrid"), ("onsite","On-site")],
        validators=[Optional()])
    relocation = BooleanField("Open to relocation")
    authorization = SelectField("Work Authorization (US)",
        choices=[("", "— select —"),
                 ("citizen","US Citizen"),
                 ("permanent_resident","Permanent Resident"),
                 ("visa_transfer","H1B Transfer/Similar"),
                 ("sponsorship_required","Needs Sponsorship"),
                 ("other","Other")],
        validators=[Optional()])

    # --- new: education ---
    highest_degree = SelectField("Highest Degree",
        choices=[("", "— select —"), ("hs","High school/GED"), ("assoc","Associate"),
                 ("bachelors","Bachelor's"), ("masters","Master's"), ("phd","PhD/Doctorate"),
                 ("other","Other")],
        validators=[Optional()])
    school = StringField("School",
        validators=[Optional(), Length(max=120)])
    grad_year = IntegerField("Graduation Year",
        validators=[Optional(), NumberRange(min=1950, max=2100)])

    # --- new: links ---
    portfolio = StringField("Portfolio Website",
        validators=[Optional(), URL(require_tld=True), Length(max=200)])
    github = StringField("GitHub URL",
        validators=[Optional(), URL(require_tld=True), Length(max=200), must_be_domain("github.com")])

    # --- new: extras for advanced users ---
    certifications = TextAreaField("Certifications (comma-separated or lines)",
        validators=[Optional(), Length(max=300)],
        filters=[lambda s: clean_commalist(s, 300, 15)])
    achievements = TextAreaField("Key Achievements (bullets or sentences)",
        validators=[Optional(), Length(max=600)])
    languages = StringField("Languages (comma-separated)",
        validators=[Optional(), Length(max=200)],
        filters=[lambda s: clean_commalist(s, 200, 20)])
