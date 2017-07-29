import datetime
from functools import wraps

import jwt
from flask import request, jsonify, current_app

from . import api
from .errors import bad_request, unauthorized, forbidden
from ..models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return unauthorized('Token is missing.')
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except jwt.ExpiredSignatureError:
            return unauthorized('Token is expired.')
        except:
            return forbidden('Token is invalid.')
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
    return unauthorized('Could not verify.')


@api.route('/refresh_token')  # token for 8 hours
def get_refresh_token():
    auth = request.authorization
    token = request.args.get('token')
    if User.check_auth(auth.username, auth.password):
        if token:
            try:
                jwt.decode(token, current_app.config['SECRET_KEY'])
                return bad_request('Token is not expired.')
            except jwt.ExpiredSignatureError:
                token = jwt.encode({
                    'user': auth.username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                }, current_app.config['SECRET_KEY'])
                return jsonify({'token': token.decode('UTF-8')})
        return bad_request('Token is missing.')
    return unauthorized('Could not verify.')
