from flask import Flask, render_template, request, send_file, flash
from wtforms import Form, StringField, TextAreaField, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional
import os
from generators.docx_builder import build_docx
import io, json

app = Flask(__name__)
from flask_wtf import CSRFProtect, FlaskForm
CSRFProtect(app)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-insecure")
from flask_wtf import CSRFProtect, FlaskForm
CSRFProtect(app)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-insecure")

# ---- subforms
class ExperienceForm(Form):
    class Meta:
        csrf = False
    title = StringField("Job Title", validators=[Optional(), Length(max=120)])
    company = StringField("Company", validators=[Optional(), Length(max=120)])
    location = StringField("Location", validators=[Optional(), Length(max=120)])
    start = StringField("Start (e.g., Jan 2023)", validators=[Optional(), Length(max=40)])
    end = StringField("End (e.g., Present)", validators=[Optional(), Length(max=40)])
    bullets = TextAreaField("Achievements (one per line)", validators=[Optional(), Length(max=4000)])

class EducationForm(Form):
    class Meta:
        csrf = False
    school = StringField("School", validators=[Optional(), Length(max=120)])
    degree = StringField("Degree (e.g., B.S. in CS)", validators=[Optional(), Length(max=120)])
    grad = StringField("Graduation (e.g., 2024)", validators=[Optional(), Length(max=40)])

class ProjectForm(Form):
    class Meta:
        csrf = False
    name = StringField("Project Name", validators=[Optional(), Length(max=120)])
    description = TextAreaField("Impact/Tech (one line)", validators=[Optional(), Length(max=1000)])

class ResumeForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    title = StringField("Headline", validators=[Optional(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    location = StringField("City, State", validators=[Optional(), Length(max=80)])
    links = StringField("Links (comma separated)", validators=[Optional(), Length(max=400)])
    summary = TextAreaField("Professional Summary (3–4 lines)", validators=[Optional(), Length(max=1000)])
    skills = TextAreaField("Skills (comma separated)", validators=[Optional(), Length(max=1000)])
    experiences = FieldList(FormField(ExperienceForm), min_entries=3, max_entries=10)
    education = FieldList(FormField(EducationForm), min_entries=1, max_entries=5)
    projects = FieldList(FormField(ProjectForm), min_entries=2, max_entries=10)
    include_projects = BooleanField("Include Projects", default=True)
    include_education = BooleanField("Include Education", default=True)

def _csv(s):  # helpers
    return [x.strip() for x in (s or "").split(",") if x.strip()]

def _lines(s):
    return [x.strip() for x in (s or "").splitlines() if x.strip()]

def normalize(form: ResumeForm):
    data = {
        "name": (form.name.data or "").strip(),
        "title": (form.title.data or "").strip(),
        "email": (form.email.data or "").strip(),
        "phone": (form.phone.data or "").strip(),
        "location": (form.location.data or "").strip(),
        "links": _csv(form.links.data),
        "summary": (form.summary.data or "").strip(),
        "skills": _csv(form.skills.data),
        "experience": [],
        "education": [],
        "projects": [],
        "options": {
            "include_projects": bool(form.include_projects.data),
            "include_education": bool(form.include_education.data),
        },
    }
    for e in form.experiences.entries:
        if any([e.form.title.data, e.form.company.data, e.form.bullets.data]):
            data["experience"].append({
                "title": (e.form.title.data or "").strip(),
                "company": (e.form.company.data or "").strip(),
                "location": (e.form.location.data or "").strip(),
                "start": (e.form.start.data or "").strip(),
                "end": (e.form.end.data or "").strip(),
                "bullets": _lines(e.form.bullets.data),
            })
    for ed in form.education.entries:
        if any([ed.form.school.data, ed.form.degree.data]):
            data["education"].append({
                "school": (ed.form.school.data or "").strip(),
                "degree": (ed.form.degree.data or "").strip(),
                "grad": (ed.form.grad.data or "").strip(),
            })
    for p in form.projects.entries:
        if any([p.form.name.data, p.form.description.data]):
            data["projects"].append({
                "name": (p.form.name.data or "").strip(),
                "description": (p.form.description.data or "").strip(),
            })
    return data

@app.route("/", methods=["GET", "POST"])
def index():
    form = ResumeForm(request.form)
    if request.method == "POST" and form.validate():
        data = normalize(form)
        _ = io.BytesIO(json.dumps(data).encode("utf-8"))  # keep if you later want to save alongside
        docx_bytes = build_docx(data)
        return send_file(
            docx_bytes,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=f"{data['name'].replace(' ', '_')}_Resume.docx",
        )
    elif request.method == "POST":
        flash("Please correct errors and try again.", "error")
    return render_template("form.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)

@app.get("/healthz")
def healthz():
    return {"ok": True}, 200
