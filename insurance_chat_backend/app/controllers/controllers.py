import json

from flask import Blueprint, current_app, request, make_response, Response, g, stream_with_context

from ..const.constant import API_KEYS


bp_controllers = Blueprint('main', __name__)


def event_stream():
    stream_id = 0
    def get_stream_id():
        nonlocal stream_id
        stream_id += 1
        return stream_id
    
    cursor = g.db.cursor()
    cursor.execute("SELECT 1 AS query_test")
    test = cursor.fetchall()

    st1 = json.dumps({"type": "processing", "code": "1", "message": "ANALYZE QUERY"})
    yield f"id: {get_stream_id()}\n"
    yield f"data: {st1}\n\n"

    st2 = json.dumps({"type": "processing", "code": "2", "message": json.dumps(test)})
    yield f"id: {get_stream_id()}\n"
    yield f"data: {st2}\n\n"

    st2 = json.dumps({"type": "response", "data": "테스트 완료"}, ensure_ascii=False)
    yield f"id: {get_stream_id()}\n"
    yield f"data: {st2}\n\n"


# 챗봇 API
@bp_controllers.route("/chat", methods=['GET'])
def chat_response():
    headers = request.headers
    current_app.logger.info('[Chat API] Request query parameters %s', request.args.to_dict())

    if "Authorization" in headers:
        if headers["Authorization"] not in API_KEYS:
            return make_response(json.dumps({"status": "error", "message": "Invalid API key."}), 200)

    response = Response(stream_with_context(event_stream()), mimetype="text/event-stream; charset=utf-8")
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Cache-Control"] = "no-cache"
    return response

