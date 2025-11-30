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

            cursor.execute('SELECT content FROM `class` ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            conn.close()

            if row:
                data = json.loads(row[0])
                return jsonify(data)
            else:
                return jsonify({})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == 'POST':
        try:
            new_data = request.get_json()
            content_str = json.dumps(new_data, ensure_ascii=False)
            now = datetime.now()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO class (content, create_date, update_date) VALUES (?, ?, ?)',
                (content_str, now, now)
            )
            conn.commit()
            conn.close()
            return jsonify({"success": "Class data saved successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
