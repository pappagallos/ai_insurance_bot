import json

from flask import Blueprint, current_app, request, make_response, redirect, stream_template, Response, g, stream_with_context


bp_controllers = Blueprint('main', __name__)


# 챗봇 API
@bp_controllers.route("/chat", methods=['POST'])
def chat_response():
    print("테스트")
    return make_response(json.dumps({"result": True, "data": "테스트"}, ensure_ascii=False), 200)

