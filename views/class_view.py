import json
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from views.constants.constants import *
from views.enums.enums import *

class_bp = Blueprint('class', __name__, url_prefix='/class')


@class_bp.route('/')
def index():
    """渲染课表主页面"""
    return render_template('class/index.html')


@class_bp.route('/api', methods=['GET', 'POST'])
def handle_class_data():
    """处理课表的读取和保存请求"""
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM `class` ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            conn.close()

            if row:
                data = {
                    "id": row[0],
                    "content": json.loads(row[1]) if row[1] else None,
                    "start_date": row[2],
                    "end_date": row[3],
                    "create_date": row[4],
                    "update_date": row[5]
                }
                return jsonify(data)
            else:
                return jsonify({})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == 'POST':
        try:
            new_data = request.get_json()

            content_str = json.dumps(new_data.get("content", {}), ensure_ascii=False)
            start_date = new_data.get("start_date")
            end_date = new_data.get("end_date")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO class (content, start_date, end_date, create_date, update_date)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (content_str, start_date, end_date, now, now)
            )
            conn.commit()
            conn.close()

            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
