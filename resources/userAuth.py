import sys
sys.path.append('resources')
import globalS
import generic
import loggerRecord
from functools import wraps
from flask import abort, request
logger =  loggerRecord.get_logger()
#http://flask.pocoo.org/snippets/8/

#from itsdangerous import Signer,(TimedJSONWebSignatureSerializer
#                          as Serializer, BadSignature, SignatureExpired)
#from itsdangerous import URLSafeSerializer, BadSignature
#from itsdangerous import (
#     TimedJSONWebSignatureSerializer as TimedToken,
#     JSONWebSignatureSerializer as Token,
#     BadSignature, BadData
#     )
#
#
#s = Signer('secret-key')
#>>> s.sign('my string')
#'my string.wh6tMHxLgJqB6oY1uT7
#class User(db.Model):
#    # ...
#
#    def generate_auth_token(self, expiration = 600):
#        s = Serializer(globalS.dictDb['SECRET_KEY'], expires_in = expiration)
#        return s.dumps({ 'id': self.id })
#
#    @staticmethod
#    def verify_auth_token(token):
#        s = Serializer(app.config['SECRET_KEY'])
#        try:
#            data = s.loads(token)
#        except SignatureExpired:
#            return None # valid token, but expired
#        except BadSignature:
#            return None # invalid token
#        user = User.query.get(data['id'])
#        return user
#
#    def hash_password(self, password):
#        self.password_hash = pwd_context.encrypt(password)
#
#    def verify_password(self, password):
#        return pwd_context.verify(password, self.password_hash)
#
#    def is_authenticated(self):
#        return True
#
#    def is_active(self):
#        return True
#
#    def is_anonymous(self):
#        return False
#
#    def get_id(self):
#        return unicode(self.id)
#
#    def __repr__(self):
#        return '<User %r>' % (self.username)
#

def validate_token(access_token):
    '''Verifies that an access-token is valid and
    meant for this app.

    Returns None on fail, and an e-mail on success'''
    h = Http()
    resp, cont = h.request("https://www.googleapis.com/oauth2/v2/userinfo",
                           headers={'Host': 'www.googleapis.com',
                                    'Authorization': access_token})

    if not resp['status'] == '200':
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        # Running this in Python3
        # httplib2 returns byte objects
        data = json.loads(cont.decode())

    return data['email']

def requires_auth(fn):
    """Decorator that checks that requests contain an id-token in the request header.
    userid will be None if the authentication failed, and have an id otherwise.

    Usage:
    @app.route("/")
    @authorized
    def secured_root(userid=None):
        pass
    """
    #@wraps(fn)
    def _wrap(*args, **kwargs):
        if 'Authorization' not in request.headers:
            # Unauthorized
            logger.warn("No token in header")
            abort(401)
            return None


        logger.debug("Checking token...")
        userid = validate_token(request.headers['Authorization'])
        if userid is None:
            logger.warn("Check returned FAIL!")
            # Unauthorized
            abort(401)
            return None

        return fn(userid=userid, *args, **kwargs)
    return _wrap

#login_manager = LoginManager()
#login_manager.init_app(app)
#
#@login_manager.request_loader
#def load_user(request):
#    token = request.headers.get('Authorization')
#    if token is None:
#        token = request.args.get('token')
#
#    if token is not None:
#        username,password = token.split(":") # naive token
#        user_entry = User.get(username)
#        if (user_entry is not None):
#            user = User(user_entry[0],user_entry[1])
#            if (user.password == password):
#                return user
#    return None
#
#@app.route("/protected/",methods=["GET"])
#@login_required
#def protected():
#    return Response(response="Hello Protected World!", status=200)


#@login_manager.user_loader
#def load_user(user_id):
#    return User.get(user_id)
#MongoDB Config
#app.config['MONGODB_DB'] = 'wowgicflaskapp'
#app.config["MONGODB_HOST"] = 'mongodb://localhost:27017/wowgicflaskapp'
#app.config["MONGODB_DB"] = True
#app.config['MONGODB_HOST'] = 'localhost'
#app.config['MONGODB_PORT'] = 27017
#app.config['WTF_CSRF_ENABLED'] = False
#app.config['MONGODB_SETTINGS'] = {
#    'db': 'wowgicflaskapp',
#    'host': 'mongodb://localhost:27017/wowgicflaskapp'
#}
#app.config['SECURITY_TRACKABLE '] = True

# Create database connection object
#db = MongoEngine(app)
#auth = HTTPBasicAuth()
#logger.debug("mongoEngine db object: %s",db)
#class Role(db.Document, RoleMixin):
#    name = db.StringField(max_length=80, unique=True)
#    description = db.StringField(max_length=255)

#class User(db.Document, UserMixin):
#    email = db.StringField(max_length=255)
#    password = db.StringField(max_length=255)
#    active = db.BooleanField(default=True)
#    userId = db.IntField()
#    confirmed_at = db.DateTimeField()
#    last_login_at = db.DateTimeField()
#    current_login_at = db.DateTimeField()
#    # Why 45 characters for IP Address ?
#    # See http://stackoverflow.com/questions/166132/maximum-length-of-the-textual-representation-of-an-ipv6-address/166157#166157
#    last_login_ip = db.StringField(max_length=45)
#    current_login_ip = db.StringField(max_length=45)
#    login_count = db.IntField()
#    roles = db.ListField(db.ReferenceField(Role), default=[])

#    def generate_auth_token(self, expiration = 600):
#        s = Serializer(globalS.dictDb['SECRET_KEY'], expires_in = expiration)
#        logger.debug('generate_auth_token:%s', s.dumps({ 'id': self.id }))
#        return s.dumps({ 'id': self.id })
#
#    @staticmethod
#    def verify_auth_token(token):
#        s = Serializer(globalS.dictDb['SECRET_KEY'])
#        try:
#            data = s.loads(token)
#        except SignatureExpired:
#            return None # valid token, but expired
#        except BadSignature:
#            return None # invalid token
#        user = User.query.get(data['id'])
#        return user
#
#    def __repr__(self):
#        return '<User %r>' % self.userId
#
## Setup Flask-Security
#user_datastore = MongoEngineUserDatastore(db, User, Role)
#security = Security(app, user_datastore)

#@auth.verify_password
#def verify_password(username_or_token, password):
#    # first try to authenticate by token
#    user = User.verify_auth_token(username_or_token)
#    if not user:
#        # try to authenticate with username/password
#        user = User.query.filter_by(username=username_or_token).first()
#        if not user or not user.verify_password(password):
#            return False
#    g.user = user
#    return True

#@app.route('/api/resource')
#def get_resource():
#    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

#@app.before_request
#def before_request():
#    g.user = current_user

#@app.before_first_request
#def create_user():
#    #user_datastore.create_user(, )
#    user_datastore.create_user(userId="88888888888",email='test@example.com',password='test123')
#
#@app.route('/api/resource')
#@auth.login_required
#def get_resource():
#    return ('Hello, %s!' % g.user.username)
#
#@app.route('/getToken')
#def getToken():
#    #ID = request.args.get("userid")
#    user = User(userId='88888888888')
#    token = user.generate_auth_token()
#    #token = g.user.generate_auth_token()
#    return token.decode('ascii')