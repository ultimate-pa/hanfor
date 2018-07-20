from flask import jsonify, g, render_template
from hanfor import db
from hanfor.sites import bp
from hanfor.utils.nocache_decorator import nocache


@bp.route('/<site>', methods=['GET'])
def static_sites(site):
    available_sites = [
        'autocomplete',
        'help',
        'statistics',
        'variables',
        'tags'
    ]
    if site in available_sites:
            return render_template('{}.html'.format(site))
    else:
        return render_template('404.html'), 404
