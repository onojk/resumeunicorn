# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Optional,
    Regexp,
    ValidationError,
    AnyOf,
)
from urllib.parse import urlparse

# Safe characters for short text fields like "role", "school", "location"
SAFE_TEXT_RE = r'^[A-Za-z0-9 ,./&()+#\-]{2,100}$'

def must_be_linkedin(form, field):
    """Require a linkedin.com (or linkedin.cn) URL if provided."""
    if not field.data:
        return
    u = urlparse(field.data)
    host = (u.hostname or "").lower()
    if not (host.endswith("linkedin.com") or host.endswith("linkedin.cn")):
        raise ValidationError("Must be a linkedin.com URL")

def must_be_github(form, field):
    """Require a github.com URL if provided."""
    if not field.data:
        return
    u = urlparse(field.data)
    host = (u.hostname or "").lower()
    if not host.endswith("github.com"):
        raise ValidationError("Must be a github.com URL")

class ResumeRequestForm(FlaskForm):
    # --- Identity / contact ---
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=100)],
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(min=7, max=20),
            Regexp(r"^[0-9+()\- .]{7,20}$", message="Enter a valid phone number"),
        ],
    )

    location = StringField(
        "Location",
        validators=[Optional(), Regexp(SAFE_TEXT_RE)],
    )

    # --- Role / links ---
    role = StringField(
        "Target Role",
        validators=[DataRequired(), Regexp(SAFE_TEXT_RE)],
    )

    linkedin = StringField(
        "LinkedIn",
        validators=[Optional(), must_be_linkedin],
    )

    github = StringField(
        "GitHub",
        validators=[Optional(), must_be_github],
    )

    portfolio = StringField(
        "Portfolio / Website",
        validators=[Optional(), Length(max=200)],
    )

    # --- Education ---
    school = StringField(
        "School",
        validators=[Optional(), Regexp(SAFE_TEXT_RE)],
    )

    highest_degree = RadioField(
        "Highest Degree",
        choices=[
            ("hs", "High School"),
            ("aa", "Associate"),
            ("ba", "Bachelor's"),
            ("ms", "Master's"),
            ("phd", "PhD"),
            ("bootcamp", "Bootcamp"),
            ("other", "Other"),
        ],
        validators=[Optional(), AnyOf(["hs", "aa", "ba", "ms", "phd", "bootcamp", "other"])],
    )

    grad_year = StringField(
        "Graduation Year",
        validators=[Optional(), Regexp(r"^(19|20)\d{2}$", message="Use a 4-digit year")],
    )

    years = StringField(  # years of experience
        "Years of Experience",
        validators=[Optional(), Regexp(r"^\d{1,2}(\.\d)?$", message="e.g., 5 or 5.5")],
    )

    # --- Free-text sections ---
    skills = TextAreaField(
        "Skills",
        validators=[Optional(), Length(max=2000)],
    )

    languages = TextAreaField(
        "Languages",
        validators=[Optional(), Length(max=2000)],
    )

    achievements = TextAreaField(
        "Achievements",
        validators=[Optional(), Length(max=4000)],
    )

    certifications = TextAreaField(
        "Certifications",
        validators=[Optional(), Length(max=2000)],
    )

    summary = TextAreaField(
        "Summary",
        validators=[Optional(), Length(max=2000)],
    )

    # --- Selectors toggles expected by the template ---
    authorization = RadioField(
        "Work Authorization",
        choices=[
            ("us", "US Citizen"),
            ("gc", "Green Card"),
            ("ead", "EAD"),
            ("h1b", "H-1B"),
            ("tn", "TN"),
            ("e3", "E-3"),
            ("other", "Other"),
        ],
        validators=[Optional(), AnyOf(["us", "gc", "ead", "h1b", "tn", "e3", "other"])],
    )

    relocation = RadioField(
        "Open to Relocation",
        choices=[("yes", "Yes"), ("no", "No"), ("maybe", "Maybe")],
        validators=[Optional(), AnyOf(["yes", "no", "maybe"])],
    )

    work_mode = RadioField(
        "Work mode",
        choices=[("onsite", "On-site"), ("hybrid", "Hybrid"), ("remote", "Remote")],
        validators=[Optional(), AnyOf(["onsite", "hybrid", "remote"])],
    )

    # --- Theme (used by rendering and PDF) ---
    theme = RadioField(
        "Theme",
        choices=[
            ("emerald", "Emerald"),
            ("sapphire", "Sapphire"),
            ("slate", "Slate"),
            ("rose", "Rose"),
        ],
        default="emerald",
        validators=[DataRequired(), AnyOf(["emerald", "sapphire", "slate", "rose"])],
    )
