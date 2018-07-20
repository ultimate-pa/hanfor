from flask import jsonify, g
from hanfor import db
from hanfor.api import bp
from hanfor.models import Variable
from hanfor.utils.nocache_decorator import nocache


@bp.route('/test', methods=['GET'])
@nocache
def test():
    var = Variable.query.all()[0]
    db.session.commit()

    return jsonify({'vars': var.name})
