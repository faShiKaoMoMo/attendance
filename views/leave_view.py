import math
from datetime import datetime
import sqlite3
from views.constants.constants import *

from flask import Blueprint, render_template, request, jsonify

leave_bp = Blueprint('leave', __name__, url_prefix='/leave')


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
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT status, COUNT(*) as cnt FROM leave GROUP BY status')
        rows = cursor.fetchall()
        conn.close()

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
        description = req_data.get("description")
        status = req_data.get("status")
        now = datetime.now()

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leave (name, start_date, end_date, 
            status, description, create_date, update_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, start_date, end_date,
                  status, description, now, now))

        _id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "请假记录新增成功", "id": _id})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/update', methods=['POST'])
def handle_update_request():
    try:
        req_data = request.get_json()
        _id = req_data.get("id")
        name = req_data.get("name")
        start_date = req_data.get("start_date")
        end_date = req_data.get("end_date")
        description = req_data.get("description")
        status = req_data.get("status")
        now = datetime.now()

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE leave
            SET name=?, start_date=?, end_date=?, status=?, description=?, update_date=?
            WHERE id=?
            """, (name, start_date, end_date, status, description, now, _id))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "请假记录更新成功"})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/approval', methods=["POST"])
def handle_approval_request():
    try:
        req_data = request.get_json()
        _id = req_data.get("id")
        status = req_data.get("status")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
                UPDATE leave
                SET status=?
                WHERE id=?
                """, (status, _id))

        conn.commit()
        cursor.close()

        return jsonify({"success": True, "message": "审核操作成功!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leave_bp.route('/list', methods=["GET"])
def handle_get_data_by_page():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 计算总数据量
        total = 0
        cursor.execute('SELECT COUNT(*) FROM leave')
        total = cursor.fetchone()[0]

        pageNo = int(request.args.get("pageNo"))
        pageSize = int(request.args.get("pageSize"))
        # 计算偏移量
        offset = (pageNo - 1) * pageSize
        cursor.execute("""
        SELECT * FROM leave ORDER BY start_date DESC LIMIT ? OFFSET ?
        """, (pageSize, offset))
        rows = cursor.fetchall()
        conn.close()

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
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        _id = request.args.get("id")

        cursor.execute("""
        SELECT * FROM leave WHERE id=?
        """, (_id,))
        row = cursor.fetchone()
        conn.close()

        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

