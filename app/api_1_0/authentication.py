import datetime
from functools import wraps
from flask import request, make_response, jsonify, current_app
import jwt
from . import api


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing.'}), 403
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid.'}), 403
        return f(*args, **kwargs)
    return decorated


@api.route('/token')
def login():
    auth = request.authorization
    if auth and auth.password == 'password' and auth.username == 'Maxim':
        token = jwt.encode({'user': auth.username,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           current_app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
