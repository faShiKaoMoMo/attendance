import json
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from views.constants.constants import *
from views.enums.enums import *

config_bp = Blueprint('config', __name__, url_prefix='/config')


@config_bp.route('/')
def index():
    """渲染考勤配置主页面"""
    return render_template('config/index.html')


@config_bp.route('/lab/list', methods=['GET'])
def list_config_data():
    try:
        pageNo = int(request.args.get('pageNo', 1))  # 当前页，默认为1
        pageSize = int(request.args.get('pageSize', 10))  # 每页条数，默认为10
        offset = (pageNo - 1) * pageSize

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM attendance_config ORDER BY id DESC LIMIT ? OFFSET ?', (pageSize, offset))
            rows = cursor.fetchall()

        data = []
        for row in rows:
            excluded_list = []
            if row["excluded_name"]:
                try:
                    excluded_list = json.loads(row["excluded_name"])
                except Exception:
                    excluded_list = [name.strip() for name in row["excluded_name"].split(',') if name.strip()]
            data.append({
                "id": row["id"],
                "name": row["name"],
                "lab": row["lab"],
                "excluded_name": excluded_list
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/lab/add', methods=['POST'])
def add_config_data():
    try:
        req_data = request.get_json()
        name = req_data.get("name")
        lab = req_data.get("lab")
        excluded_name = req_data.get("excluded_name", [])

        if not name or not lab:
            return jsonify({"success": False, "error": "name 与 lab 不能为空"}), 400

        excluded_str = json.dumps(excluded_name, ensure_ascii=False)
        now = datetime.now()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance_config (name, lab, excluded_name, create_date, update_date)
                VALUES (?, ?, ?, ?, ?)
            """, (name, lab, excluded_str, now, now))

        return jsonify({"success": True, "message": "配置已成功保存"})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/lab/<int:lab_id>/delete', methods=['POST'])
def delete_config_data(lab_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance_config WHERE id = ?", (lab_id,))
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "未找到指定的 ID，删除失败"}), 404

        return jsonify({"success": True, "message": "配置已成功删除"})
    except Exception as e:
        print(f"An error occurred during deletion: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


####################################################################################################

@config_bp.route('/account/list', methods=['GET'])
def list_account_data():
    try:
        pageNo = int(request.args.get('pageNo', 1))  # 当前页，默认为1
        pageSize = int(request.args.get('pageSize', 10))  # 每页条数，默认为10
        offset = (pageNo - 1) * pageSize

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM attendance_account ORDER BY id DESC LIMIT ? OFFSET ?', (pageSize, offset))
            rows = cursor.fetchall()

        data = [dict(row) for row in rows]
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/account/add', methods=['POST'])
def add_or_update_account_data():
    try:
        data = request.get_json()
        _id = data.get("id")
        name = data.get("name")
        mobile = data.get("mobile")
        password = data.get("password")
        email = data.get("email")
        now = datetime.now()

        if not name or not mobile or not password:
            return jsonify({"success": False, "error": "名称, 手机号 和 密码 不能为空"}), 400

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            if _id:
                # 更新已有账号
                cursor.execute("""
                    UPDATE attendance_account
                    SET name=?, mobile=?, password=?, email=?, update_date=?
                    WHERE id=?
                """, (name, mobile, password, email, now, _id))
            else:
                # 插入新账号
                cursor.execute("""
                    INSERT INTO attendance_account (name, mobile, password, email, create_date, update_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, mobile, password, email, now, now))

        return jsonify({"success": True, "message": "账号已成功保存"})
    except sqlite3.IntegrityError as e:
        return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 409
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/account/<int:account_id>/delete', methods=['POST'])
def delete_account_data(account_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # 执行删除操作
            cursor.execute("DELETE FROM attendance_account WHERE id = ?", (account_id,))

            # 检查是否成功删除（rowcount > 0 表示有数据被删除）
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "未找到指定的账号 ID，删除失败"}), 404

        return jsonify({"success": True, "message": "账号已成功删除"})

    except Exception as e:
        print(f"An error occurred during account deletion: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


####################################################################################################

@config_bp.route('/calendar/list', methods=['GET'])
def list_calendar_data():
    """
    分页获取日历配置表 calendar_override 的记录
    GET -> 返回分页后的日历记录
    """
    try:
        # 获取分页参数，默认第一页，每页10条数据
        pageNo = int(request.args.get('pageNo', 1))
        pageSize = int(request.args.get('pageSize', 10))

        offset = (pageNo - 1) * pageSize  # 计算分页偏移量

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询总记录数
            cursor.execute('SELECT COUNT(*) FROM calendar_override')
            total_records = cursor.fetchone()[0]

            # 查询分页数据
            cursor.execute("""
                SELECT * FROM calendar_override
                ORDER BY date DESC
                LIMIT ? OFFSET ?
            """, (pageSize, offset))
            rows = cursor.fetchall()

        # 将结果转为字典列表
        data = [dict(row) for row in rows]
        return jsonify({
            "success": True,
            "data": data,
            "totalRecords": total_records,
            "pageNo": pageNo,
            "pageSize": pageSize
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/calendar/add', methods=['POST'])
def add_calendar_data():
    """
    新增日历配置记录
    POST -> 新增日历记录
    """
    try:
        data = request.get_json()
        date = data.get("date")
        type = data.get("type")
        swap_date = data.get("swap_date", None)
        description = data.get("description", "")
        now = datetime.now()

        if not date or not type:
            return jsonify({"success": False, "error": "日期和类型不能为空"}), 400

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            if type == CalendarTypeEnum.SWAP.code and swap_date:
                # 插入两条交换记录
                cursor.execute("""
                    INSERT INTO calendar_override (date, type, swap_date, description, create_date, update_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (date, type, swap_date, description, now, now))
                cursor.execute("""
                    INSERT INTO calendar_override (date, type, swap_date, description, create_date, update_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (swap_date, type, date, description, now, now))
            else:
                # 插入新日历记录
                cursor.execute("""
                    INSERT INTO calendar_override (date, type, description, create_date, update_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, type, description, now, now))

        return jsonify({"success": True, "message": "调课记录已成功保存"})
    except sqlite3.IntegrityError as e:
        return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 409
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/calendar/<int:calendar_id>/delete', methods=['POST'])
def delete_calendar_data(calendar_id):
    """
    删除日历配置记录
    POST -> 删除指定ID记录（如果是调休SWAP，会自动删除关联的另一条记录）
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # 1. 先查询要删除的记录详情
            cursor.execute("SELECT date, type, swap_date FROM calendar_override WHERE id = ?", (calendar_id,))
            row = cursor.fetchone()

            if not row:
                return jsonify({"success": False, "error": "未找到指定的记录"}), 404

            current_date, current_type, current_swap_date = row

            # 2. 删除当前指定的记录
            cursor.execute("DELETE FROM calendar_override WHERE id = ?", (calendar_id,))
            deleted_count = cursor.rowcount

            # 3. 联动删除逻辑：如果是调休(SWAP)且有对应的交换日期
            if current_type == CalendarTypeEnum.SWAP.code and current_swap_date:
                cursor.execute("""
                    DELETE FROM calendar_override 
                    WHERE date = ? AND type = ? AND swap_date = ?
                """, (current_swap_date, current_type, current_date))
                deleted_count += cursor.rowcount

        return jsonify({
            "success": True,
            "message": f"删除成功，共清理 {deleted_count} 条记录"
        })
    except Exception as e:
        print(f"An error occurred during calendar deletion: {e}")
        return jsonify({"success": False, "error": str(e)}), 500