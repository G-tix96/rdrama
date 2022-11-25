import os
from collections import Counter
from json import loads
from shutil import copyfile
import xml

import gevent

from files.classes import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.const import *
from files.helpers.get import *
from files.helpers.marsify import marsify
from files.helpers.media import *
from files.helpers.owoify import owoify
from files.helpers.regex import *
from files.helpers.sanitize import filter_emojis_only
from files.helpers.slots import *
from files.helpers.treasure import *
from files.routes.front import comment_idlist
from files.routes.routehelpers import execute_shadowban_viewers_and_voters
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

import xml.etree.ElementTree as ET

tree = ET.parse('docs/api.xml')

@app.get("/dev/api")
def get_docs_page():
    root = tree.getroot()

    return render_template("docs.html", root=tree.getroot())
