from flask import jsonify, g
from hanfor import db
from hanfor.api import bp
from hanfor.api.response import response
from hanfor.models import Variable
from hanfor.utils.nocache_decorator import nocache


@bp.route('/var/<command>', methods=['GET'])
@nocache
def var(command):
    if command == 'gets':
        response['success'] = True
        response['errormsg'] = ''
        var = Variable.query.all()
        response['data'] = [v.to_dict() for v in var]

    return jsonify(response)
