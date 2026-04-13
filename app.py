import os
from flask import Flask, jsonify, request, send_from_directory
from database import init_db, create_task, get_all_tasks, get_task, update_task, delete_task

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")


def create_app(db_path: str = DEFAULT_DB_PATH) -> Flask:
    app = Flask(__name__, static_folder="static")
    app.config["DB_PATH"] = db_path
    init_db(db_path)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        tasks = get_all_tasks(app.config["DB_PATH"])
        return jsonify(tasks), 200

    @app.route("/tasks", methods=["POST"])
    def add_task():
        body = request.get_json(silent=True) or {}
        title = (body.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title is required and cannot be empty"}), 400
        task = create_task(app.config["DB_PATH"], title)
        return jsonify(task), 201

    @app.route("/tasks/<task_id>", methods=["PATCH"])
    def edit_task(task_id):
        if get_task(app.config["DB_PATH"], task_id) is None:
            return jsonify({"error": "task not found"}), 404
        body = request.get_json(silent=True) or {}
        title = body.get("title")
        completed = body.get("completed")
        if title is not None and not str(title).strip():
            return jsonify({"error": "title cannot be empty"}), 400
        if title is not None:
            title = str(title).strip()
        updated = update_task(app.config["DB_PATH"], task_id, title=title, completed=completed)
        if updated is None:
            return jsonify({"error": "task not found"}), 404
        return jsonify(updated), 200

    @app.route("/tasks/<task_id>", methods=["DELETE"])
    def remove_task(task_id):
        deleted = delete_task(app.config["DB_PATH"], task_id)
        if not deleted:
            return jsonify({"error": "task not found"}), 404
        return "", 204

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, port=5000)
