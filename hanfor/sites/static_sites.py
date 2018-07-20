from flask import jsonify, g, render_template
from hanfor import db
from hanfor.sites import bp
from hanfor.utils.nocache_decorator import nocache


@bp.route('/<name>', methods=['GET'])
def static_sites(name):
    available_sites = [
        'autocomplete',
        'help',
        'statistics',
        'variables',
        'tags'
    ]
    if name in available_sites:
            return render_template('simple.html'.format(name))
    else:
        return render_template('404.html'), 404
