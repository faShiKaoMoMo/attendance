from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, render_template, request, jsonify

from views.service.crawler import *
from views.service.excelsaver import *
from views.service.statistics import *

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

executor = ThreadPoolExecutor(max_workers=2)


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
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO attendance_statistics (params, result, status, create_date, update_date)
                VALUES (?, ?, ?, ?, ?)
            """, (params_str, None, StatisticsEnum.RUNNING.code, now, now))

            new_id = cursor.lastrowid

            conn.commit()
            conn.close()

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
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM attendance_statistics WHERE id = ?", (id,))
        row = cursor.fetchone()

        conn.close()

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


@attendance_bp.route('/statistics/<int:id>/captcha', methods=['POST'])
def update_captcha(id):
    """
    接收 captcha 数据并将其写入指定ID的记录中。
    """
    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"success": False, "error": "Request body 不能为空"}), 400

        captcha = req_data.get('captcha')
        if not captcha:
            return jsonify({"success": False, "error": "请求中必须包含 'captcha' 字段"}), 400

        now = datetime.now()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE attendance_statistics
            SET captcha = ?, status=?, update_date = ?
            WHERE id = ?
        """, (captcha, StatisticsEnum.RUNNING.code, now, id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"success": False, "error": f"未找到ID为 {id} 的数据"}), 404

        conn.commit()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def execute(_id, req_data):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        toke = token(conn, cursor, _id, req_data)
        data = fetch(conn, cursor, toke, req_data)
        file = excel(conn, cursor, data, req_data)

        cursor.execute("""
            UPDATE attendance_statistics
            SET result=?, status=?, update_date=?
            WHERE id=?
        """, ("", StatisticsEnum.SUCCESS.code, datetime.now(), _id))
        conn.commit()

    except Exception as e:
        traceback.print_exc()
        cursor.execute("""
            UPDATE attendance_statistics
            SET status=?, message=?, update_date=?
            WHERE id=?
        """, (StatisticsEnum.FAILED.code, str(e), datetime.now(), _id))
        conn.commit()

    finally:
        conn.close()
