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


@config_bp.route('/api', methods=['GET', 'POST'])
def handle_config_data():
    """
    处理考勤配置表 attendance_config 的读取和保存请求。
    GET  -> 返回所有配置记录
    POST -> 新增或修改配置（依据是否传入 id）
    """
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM attendance_config ORDER BY id DESC')
            rows = cursor.fetchall()
            conn.close()

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

    elif request.method == 'POST':
        try:
            req_data = request.get_json()
            _id = req_data.get("id")
            name = req_data.get("name")
            lab = req_data.get("lab")
            excluded_name = req_data.get("excluded_name", [])

            if not name or not lab:
                return jsonify({"success": False, "error": "name 与 lab 不能为空"}), 400

            excluded_str = json.dumps(excluded_name, ensure_ascii=False)
            now = datetime.now()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            if _id:
                cursor.execute("""
                        UPDATE attendance_config
                        SET name=?, lab=?, excluded_name=?, update_date=?
                        WHERE id=?
                    """, (name, lab, excluded_str, now, _id))
            else:
                cursor.execute("""
                        INSERT INTO attendance_config (name, lab, excluded_name, create_date, update_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, lab, excluded_str, now, now))
            conn.commit()
            conn.close()

            return jsonify({"success": True, "message": "配置已成功保存"})
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"success": False, "error": str(e)}), 500


@config_bp.route('/account', methods=['GET', 'POST'])
def handle_account_data():
    """
    处理账号配置表 attendance_account 的读取和保存请求。
    GET  -> 返回所有账号记录
    POST -> 新增或修改账号（依据是否传入 id）
    """
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 只选择需要的字段，避免暴露所有信息
            cursor.execute('SELECT * FROM attendance_account ORDER BY id DESC')
            rows = cursor.fetchall()
            conn.close()

            data = [dict(row) for row in rows]
            return jsonify(data)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == 'POST':
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

            conn = sqlite3.connect(DB_FILE)
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

            conn.commit()
            conn.close()

            return jsonify({"success": True, "message": "账号已成功保存"})
        except sqlite3.IntegrityError as e:
            return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 409
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"success": False, "error": str(e)}), 500