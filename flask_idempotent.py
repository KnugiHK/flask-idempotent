import uuid
import threading
from datetime import datetime, timedelta
import copy
import six
from flask import _request_ctx_stack, request, abort, wrappers
from jinja2 import Markup

class Key(object):
    def __init__(self, expiry, response):
        if not isinstance(expiry, int):
            raise TypeError('Argument "expiry" must be a string but %s was given' % type(expiry))
        if not isinstance(response, bytes) and not isinstance(response, wrappers.Response):
            raise TypeError('Argument "response" must be a Flask Response object or processing byte but %s was given' % type(response))
        self.expiry = datetime.now() + timedelta(seconds=expiry)
        self.response = response

class KeyStore(object):
    def __init__(self, app):
        super(KeyStore, self).__init__()
        self.interval = timedelta(seconds=app.config.get('IDEMPOTENT_EXPIRE') * 1.9) #Clean up interval = Expiry * 1.9 (Just in case some keys are being renew)
        self.collection = {}
        self.last_cleanup = datetime.now()
    
    def set(self, key, expiry, response):
        if not isinstance(key, str):
            raise TypeError('Argument "key" must be a string but %s was given' % type(key))
        self.collection[key] = Key(expiry, response)
        return False, "adasds"
        
    def get(self, key):
        #Clean up the expired key first to free memery
        delete_time = datetime.now()
        if self.last_cleanup + self.interval < delete_time:
            self.clean(delete_time)

        if key in self.collection:
            return self.collection[key]
        else:
            return None
    
    def clean(self, delete_time):
        def func():
            to_be_deleted = []
            for k, v in self.collection.items():
                if v.expiry < delete_time:
                    to_be_deleted.append(k)
            for k in to_be_deleted:
                self.collection.pop(k)
        t = threading.Thread(target=func)
        t.start()

class Idempotent(object):
    _PROCESSING = b'__IDEMPOTENT_PROCESSING' if six.PY3 else '__IDEMPOTENT_PROCESSING'

    def __init__(self, app=None):
        self.app = app
        self._key_finders = [lambda request: request.values.get('__idempotent_key', None),
                             lambda request: request.headers.get('X-Idempotent-Key', None)]
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.config.setdefault("IDEMPOTENT_TIMEOUT", 10)
        app.config.setdefault("IDEMPOTENT_EXPIRE", 5)

        @app.context_processor
        def template_context():
            return {'idempotent_key': self.generate_idempotent_key,
                    'idempotent_input': self.make_idempotent_input}

        app.before_request(self._before_request)
        app.after_request(self._after_request)
        self.key_collection = KeyStore(app)

    def generate_idempotent_key(self):
        return uuid.uuid4().hex

    def make_idempotent_input(self):
        return Markup('<input type="hidden" name="__idempotent_key" value="%s"/>' % self.generate_idempotent_key())

    def _find_idempotency_key(self, request):
        for func in self._key_finders:
            key = func(request)
            if key:
                return key

    def key_finder(self, func):
        self._key_finders.append(func)

    def _before_request(self):
        key = self._find_idempotency_key(request)
        if not key:
            return
        key = 'IDEMPOTENT_{}'.format(key)
        res = self.key_collection.get(key)
        if not res:
            # We are the first to get this request... Lets go ahead and run the request
            setattr(_request_ctx_stack.top, '__idempotent_key', key)
            self.key_collection.set(key, self.app.config.get('IDEMPOTENT_EXPIRE'), self._PROCESSING)
            return  # Tell flask to continue
        else:
            if hasattr(res, 'expiry') and res.expiry < datetime.now():
                setattr(_request_ctx_stack.top, '__idempotent_key', key)
                return
            if res.response == self._PROCESSING:
                endtime = datetime.now() + timedelta(seconds=self.app.config.get('IDEMPOTENT_TIMEOUT'))
                while datetime.now() < endtime:
                    res = self.key_collection.get(key)
                    if res.response != self._PROCESSING:
                        break
            res = self.key_collection.get(key)
            if res.response == self._PROCESSING:
                abort(408)
            return res.response

    def _after_request(self, response):
        if hasattr(_request_ctx_stack.top, '__idempotent_key'):
            key = getattr(_request_ctx_stack.top, '__idempotent_key')
            # Save the request in memery, notify, then return
            self.key_collection.set(key, self.app.config.get('IDEMPOTENT_EXPIRE'), response)
        return response