from flask import Blueprint

bp = Blueprint('api', __name__)

from hanfor.api import variable, tools
