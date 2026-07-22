import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

_wrapped = None

def application(environ, start_response):
    global _wrapped
    if _wrapped is None:
        from a2wsgi import ASGIMiddleware
        from app.main import app as _asgi_app
        _wrapped = ASGIMiddleware(_asgi_app)
    return _wrapped(environ, start_response)
    