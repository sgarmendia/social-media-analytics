from flask import Response
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

def response(data, status: int = 200):
    return Response(
        dumps(data, json_options=RELAXED_JSON_OPTIONS),
        status,
        mimetype="application/json",
        content_type="application/json"
    )