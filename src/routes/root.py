# from flask import request
from utils.response import response
# from decorators.errors import handle_error
# from controllers.root import process_tweet
from app import app


@app.route("/analyze/<txt>")
# @handle_error
# @validate_route
def process_term(txt):
    # res = get_all(collection)
    return response(txt)


# @app.route("/<collection>/<id>", methods=["PATCH"])
# # @handle_error
# # @validate_route
# def patch_collection_id(collection, id):
#     body = request.get_json()
#     # validate json keys

#     res = find_by_id_and_update(collection, id, body)
#     return response(res)