from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os
import sqlite3
import traceback

from flask import Blueprint, render_template, request, jsonify, send_file

from views.service.crawler import *
from views.service.excelsaver import *
from views.service.statistics import *

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

executor = ThreadPoolExecutor(max_workers=2)
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@attendance_bp.route('/')
def index():
    """
    渲染考勤管理的主页面。
    它会去 templates/attendance/ 文件夹下寻找 index.html 文件。
    """
    return render_template('attendance/index.html')


@attendance_bp.route('/statistics', methods=['POST'])
def statistics():
    """
    接收统计请求，创建一条新的统计任务记录。
    """
    if request.method == 'POST':
        try:
            req_data = request.get_json()
            if not req_data:
                return jsonify({"error": "Request body 不能为空"}), 400
            params_str = json.dumps(req_data, ensure_ascii=False)

            now = datetime.now()

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO attendance_statistics (params, result, status, create_date, update_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (params_str, None, StatisticsEnum.RUNNING.code, now, now))

                new_id = cursor.lastrowid

            executor.submit(execute, new_id, req_data)

            return jsonify({"success": True, "id": new_id})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/statistics/<int:id>', methods=['GET'])
def get_statistics_by_id(id):
    """
    根据ID获取单条统计任务的数据。
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM attendance_statistics WHERE id = ?", (id,))
            row = cursor.fetchone()

        if row is None:
            return jsonify({"success": False, "error": f"未找到ID为 {id} 的数据"}), 404
        else:
            result_dict = dict(row)
            if result_dict.get('params'):
                result_dict['params'] = json.loads(result_dict['params'])
            if result_dict.get('result'):
                result_dict['result'] = json.loads(result_dict['result'])

            return jsonify(result_dict)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/statistics/<int:id>/download', methods=['GET'])
def download_statistics_file(id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT result FROM attendance_statistics WHERE id = ?", (id,))
            row = cursor.fetchone()

        if row is None or not row["result"]:
            return jsonify({"success": False, "error": "文件不存在"}), 404

        result = json.loads(row["result"])
        filepath = result.get("file")
        filename = result.get("filename") or f"考勤-{id}.xlsx"

        if not filepath or not os.path.exists(filepath):
            return jsonify({"success": False, "error": "文件不存在"}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def execute(_id, req_data):
    with sqlite3.connect(DB_FILE, isolation_level=None) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            toke = token(conn, cursor, _id, req_data)
            data = fetch(conn, cursor, toke, req_data)
            file_bytes = excel(conn, cursor, data, req_data)

            filename = f"考勤-{req_data['start_date']}-{req_data['end_date']}.xlsx"
            filepath = os.path.join(REPORT_DIR, f"{_id}.xlsx")
            with open(filepath, "wb") as f:
                f.write(file_bytes)

            result = json.dumps({
                "file": filepath,
                "filename": filename
            }, ensure_ascii=False)

            cursor.execute("""
                UPDATE attendance_statistics
                SET result=?, status=?, update_date=?
                WHERE id=?
            """, (result, StatisticsEnum.SUCCESS.code, datetime.now(), _id))
            conn.commit()

        except Exception as e:
            traceback.print_exc()
            cursor.execute("""
                UPDATE attendance_statistics
                SET status=?, message=?, update_date=?
                WHERE id=?
            """, (StatisticsEnum.FAILED.code, str(e), datetime.now(), _id))
            conn.commit()
