from flask import Blueprint

bp = Blueprint('sites', __name__)

from hanfor.sites import static_sites, start
