import datetime
from functools import wraps
from flask import request, make_response, jsonify, current_app, url_for
import jwt
from . import api
from ..models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing.'}), 403
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired.',
                            'refresh_url': url_for('api.get_refresh_token')}), 401
        except:
            return jsonify({'message': 'Token is invalid.'}), 403
        return f(*args, **kwargs)
    return decorated


@api.route('/token')  # token for 30 minutes
def get_access_token():
    auth = request.authorization
    if User.check_auth(auth.username, auth.password):
        token = jwt.encode({'user': auth.username,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           current_app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@api.route('/refresh_token')  # token for 8 hours
def get_refresh_token():
    auth = request.authorization
    token = request.args.get('token')
    if User.check_auth(auth.username, auth.password):
        if token:
            try:
                jwt.decode(token, current_app.config['SECRET_KEY'])
                return jsonify({'message': 'Token is not expired'})
            except jwt.ExpiredSignatureError:
                token = jwt.encode({
                    'user': auth.username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                }, current_app.config['SECRET_KEY'])
                return jsonify({'token': token.decode('UTF-8')})
        return jsonify({'message': 'Token is missing.'}), 401
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
