import math
from datetime import datetime
import sqlite3
from views.constants.constants import *

from flask import Blueprint, render_template, request, jsonify

travel_bp = Blueprint('travel', __name__, url_prefix='/travel')


@travel_bp.route('/')
def index():
    """
    渲染出差统计主页面
    它会去 templates/travel/ 文件夹下寻找 index.html 文件。
    """
    return render_template('travel/index.html')


@travel_bp.route('/counts', methods=['GET'])
def handle_request_count():
    """
    返回各种状态的出差请求
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT status, COUNT(*) as cnt FROM travel GROUP BY status')
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


@travel_bp.route('/add', methods=['POST'])
def handle_add_request():
    try:
        req_data = request.get_json()
        name = req_data.get("name")
        destination = req_data.get("destination")
        reason = req_data.get("reason")
        start_date = req_data.get("start_date")
        end_date = req_data.get("end_date")
        description = req_data.get("description")
        avg_working_hours = req_data.get("avg_working_hours")
        status = req_data.get("status")
        now = datetime.now()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO travel (name, destination, reason, start_date, end_date, 
                status, avg_working_hours, description, create_date, update_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, destination, reason, start_date, end_date,
                      status, avg_working_hours, description, now, now))

            _id = cursor.lastrowid

        return jsonify({"success": True, "message": "出差记录新增成功", "id": _id})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@travel_bp.route('/update', methods=['POST'])
def handle_update_request():
    try:
        req_data = request.get_json()
        _id = req_data.get("id")
        name = req_data.get("name")
        destination = req_data.get("destination")
        reason = req_data.get("reason")
        start_date = req_data.get("start_date")
        end_date = req_data.get("end_date")
        description = req_data.get("description")
        status = req_data.get("status")
        now = datetime.now()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE travel
                SET name=?, destination=?, reason=?, start_date=?, end_date=?, status=?, description=?, update_date=?
                WHERE id=?
                """, (name, destination, reason, start_date, end_date,
                      status, description, now, _id))

        return jsonify({"success": True, "message": "出差记录更新成功"})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@travel_bp.route('/approval', methods=["POST"])
def handle_approval_request():
    try:
        req_data = request.get_json()
        _id = req_data.get("id")
        status = req_data.get("status")

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    UPDATE travel
                    SET status=?
                    WHERE id=?
                    """, (status, _id))

        return jsonify({"success": True, "message": "审核操作成功!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@travel_bp.route('/list', methods=["GET"])
def handle_get_data_by_page():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 计算总数据量
            cursor.execute('SELECT COUNT(*) FROM travel')
            total = cursor.fetchone()[0]

            pageNo = int(request.args.get("pageNo"))
            pageSize = int(request.args.get("pageSize"))
            # 计算偏移量
            offset = (pageNo - 1) * pageSize
            cursor.execute("""
            SELECT * FROM travel ORDER BY start_date DESC LIMIT ? OFFSET ?
            """, (pageSize, offset))
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


@travel_bp.route('/info', methods=["GET"])
def handle_get_data_by_id():
    try:
        _id = request.args.get("id")

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM travel WHERE id=?
            """, (_id,))
            row = cursor.fetchone()

        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

