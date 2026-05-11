from flask import Flask, jsonify, request, abort
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os

app = Flask(__name__)

# --- Prometheus metrics ---
REQUEST_COUNT = Counter(
    "app_request_count_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

# --- In-memory store (swap for Postgres in production) ---
todos = {}
next_id = 1

@app.before_request
def start_timer():
    request._start_time = time.time()


@app.after_request
def record_metrics(response):
    latency = time.time() - request._start_time
    REQUEST_COUNT.labels(request.method, request.path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.path).observe(latency)
    return response


@app.route("/")
def home():
    return "DevOps Flask API is running 🚀"


# --- Health & metrics endpoints ---
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# --- Todo CRUD ---
@app.route("/api/todos", methods=["GET"])
def get_todos():
    return jsonify(list(todos.values()))


@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    todo = todos.get(todo_id)
    if not todo:
        abort(404)
    return jsonify(todo)


@app.route("/api/todos", methods=["POST"])
def create_todo():
    global next_id
    data = request.get_json()
    if not data or "title" not in data:
        abort(400)
    todo = {
        "id": next_id,
        "title": data["title"],
        "done": False
    }
    todos[next_id] = todo
    next_id += 1
    return jsonify(todo), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = todos.get(todo_id)
    if not todo:
        abort(404)
    data = request.get_json()
    todo["title"] = data.get("title", todo["title"])
    todo["done"] = data.get("done", todo["done"])
    return jsonify(todo)


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    if todo_id not in todos:
        abort(404)
    del todos[todo_id]
    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
