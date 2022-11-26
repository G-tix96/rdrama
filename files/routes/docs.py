import xml
import xml.etree.ElementTree as ET
from files.__main__ import app, cache, limiter

tree = ET.parse('docs/api.xml')

@app.get("/dev/api")
@auth_desired
def get_docs_page():
    # TODO cache
    root = tree.getroot()

    return render_template("docs.html", root=tree.getroot())
