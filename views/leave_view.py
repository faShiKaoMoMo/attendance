import math
from datetime import datetime
import sqlite3
from views.constants.constants import *

from flask import Blueprint, render_template, request, jsonify

leave_bp = Blueprint('leave', __name__, url_prefix='/leave')


def build_leave_filters():
    conditions = []
    params = []

    name = (request.args.get("name") or "").strip()
    start_date = (request.args.get("start_date") or "").strip()
    end_date = (request.args.get("end_date") or "").strip()

    if name:
        conditions.append("name LIKE ?")
        params.append(f"%{name}%")
    if start_date:
        conditions.append("end_date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("start_date <= ?")
        params.append(end_date)

    where_sql = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_sql, params


@leave_bp.route('/')
def index():
    """
    渲染出差统计主页面
    它会去 templates/leave/ 文件夹下寻找 index.html 文件。
    """
    return render_template('leave/index.html')


@leave_bp.route('/counts', methods=['GET'])
def handle_request_count():
    """
    返回各种状态的出差请求
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            where_sql, params = build_leave_filters()
            cursor.execute(f'SELECT status, COUNT(*) as cnt FROM leave{where_sql} GROUP BY status', params)
            rows = cursor.fetchall()

        item_list = []
        # 记录总条数
        ans = 0
        for row in rows:
            ans += row["cnt"]
            item_list.append({
                "status": row["status"],
                "count": row["cnt"]
            })

        data = {
            "total": ans,
            "item": item_list
        }

        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/add', methods=['POST'])
def handle_add_request():
    try:
        req_data = request.get_json()
        name = req_data.get("name")
        start_date = req_data.get("start_date")
        end_date = req_data.get("end_date")
        leave_type = req_data.get("type", 2)
        description = req_data.get("description")
        status = req_data.get("status")
        now = datetime.now()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leave (name, start_date, end_date, type, status, description, create_date, update_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, start_date, end_date, leave_type, status, description, now, now))

            _id = cursor.lastrowid

        return jsonify({"success": True, "message": "请假记录新增成功", "id": _id})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/approval', methods=["POST"])
def handle_approval_request():
    try:
        req_data = request.get_json()
        _id = req_data.get("id")
        status = req_data.get("status")

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    UPDATE leave
                    SET status=?
                    WHERE id=?
                    """, (status, _id))

        return jsonify({"success": True, "message": "审核操作成功!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/list', methods=["GET"])
def handle_get_data_by_page():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            where_sql, params = build_leave_filters()
            cursor.execute(f'SELECT COUNT(*) FROM leave{where_sql}', params)
            total = cursor.fetchone()[0]

            pageNo = int(request.args.get("pageNo", 1))
            pageSize = int(request.args.get("pageSize", 10))
            offset = (pageNo - 1) * pageSize
            cursor.execute(f"""
            SELECT * FROM leave{where_sql} ORDER BY start_date DESC LIMIT ? OFFSET ?
            """, (*params, pageSize, offset))
            rows = cursor.fetchall()

        data_list = [dict(row) for row in rows]
        data = {
            "pageNo": pageNo,
            "pageSize": pageSize,
            "total": total,
            "pages": 1 if total < pageSize else math.ceil(total / pageSize),
            "list": data_list
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/info', methods=["GET"])
def handle_get_data_by_id():
    try:
        _id = request.args.get("id")

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
            SELECT * FROM leave WHERE id=?
            """, (_id,))
            row = cursor.fetchone()

        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

