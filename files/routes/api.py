import xml.etree.ElementTree as ET

from flask import render_template

from files.routes.wrappers import auth_required, auth_desired
from files.__main__ import app

tree = ET.parse('docs/api.xml')

@app.get("/api")
@auth_required
def api(v):
	return render_template("api.html", v=v)

@app.get("/api/docs")
@auth_desired
def get_docs_page():
    # TODO cache
    root = tree.getroot()

    return render_template("docs.html", root=tree.getroot())
