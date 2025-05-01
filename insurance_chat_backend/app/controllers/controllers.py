import json

from flask import Blueprint, current_app, request, make_response, Response, g, stream_with_context

from ..utils.utils import get_cosine_result, get_rerank_result, get_chat_result

from ..const.constant import API_KEYS


bp_controllers = Blueprint('main', __name__)


def get_chat_event_stream(query: str):
    stream_id = 0
    def get_stream_id():
        nonlocal stream_id
        stream_id += 1
        return stream_id
    
    documents = get_cosine_result(g.db.cursor(), query)
    documents = [json.dumps(document, ensure_ascii=False) for document in documents]
    
    # st1 = json.dumps({"type": "processing", "code": "1", "message": "FETCH RELATED DOCUMENTS"})
    # yield f"id: {get_stream_id()}\n"
    # yield f"data: {st1}\n\n"

    rerank_result = get_rerank_result(query, documents)
    # st2 = json.dumps({"type": "processing", "code": "2", "message": "RE-RANKING"})
    # yield f"id: {get_stream_id()}\n"
    # yield f"data: {st2}\n\n"

    yield from get_chat_result(query, rerank_result, get_stream_id)
    # st3 = json.dumps({"type": "processing", "code": "4", "message": "CHAT COMPLETE"})
    # yield f"id: {get_stream_id()}\n"
    # yield f"data: {st3}\n\n"


# 챗봇 API
@bp_controllers.route("/chat", methods=['POST'])
def chat_response():
    headers = request.headers
    current_app.logger.info('[Chat API] Request query parameters %s', request.json)

    api_key = None
    if "Authorization" in headers:
        if headers["Authorization"].startswith("Bearer "):
            api_key = headers["Authorization"].split(" ")[1]

        if api_key not in API_KEYS:
            return make_response(json.dumps({"status": "error", "message": "Invalid API key."}), 200)

    data = request.json
    query = data.get("query")

    if not query:
        return make_response(json.dumps({"status": "error", "message": "Invalid request."}), 400)

    response = Response(stream_with_context(get_chat_event_stream(query)), mimetype="text/event-stream; charset=utf-8")
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Cache-Control"] = "no-cache"
    return response

