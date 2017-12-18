from functools import wraps
import unicodecsv
from flask import abort, request, Response
from campaign import app

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def check_api_access(source, claim):
    """Aborts if a request does not have the correct api_token"""
    if not claim or claim != source:
        abort(401)

# Imported from http://flask.pocoo.org/snippets/8/
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']

# Imported from http://flask.pocoo.org/snippets/8/
def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

# Imported from http://flask.pocoo.org/snippets/8/
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def csv_response(headers, rows, row_type=None, row_handler=None):
    """
    Returns a response, with mimetype set to text/csv,
    given a list of headers and a two-dimensional list of rows

    The default type of row is a list or a tuple of values. If row is of type dict set the row_type.

    Accepts an optional row_handler function that can be used to transform the row.
    """
    stream = StringIO()
    if row_type == 'dict':
        csv_writer = unicodecsv.DictWriter(stream, fieldnames=headers, extrasaction='ignore')
        csv_writer.writeheader()
    else:
        csv_writer = unicodecsv.writer(stream)
        csv_writer.writerow(headers)
    if callable(row_handler):
        csv_writer.writerows(row_handler(row) for row in rows)
    else:
        csv_writer.writerows(rows)
    return Response(unicode(stream.getvalue().decode('utf-8')), mimetype='text/csv')
