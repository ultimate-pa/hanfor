from flask import jsonify
from hanfor import db
from hanfor.api import bp
from hanfor.api.response import response
from hanfor.utils.nocache_decorator import nocache


@bp.route('/tools/<command>', methods=['GET'])
@nocache
def tools(command):
    if command == 'req_file':
        response['success'] = True
        response['errormsg'] = ''
        raise NotImplementedError

    if command == 'csv_file':
        response['success'] = True
        response['errormsg'] = ''
        raise NotImplementedError

    return jsonify(response)
