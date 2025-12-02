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


@class_bp.route('/list', methods=['GET'])
def handle_class_request():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM semester_class ORDER BY id DESC')
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "name": row[1],
                "start_date": row[2],
                "end_date": row[3],
                "enable": row[4],
                "create_date": row[5],
                "update_date": row[6],
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@class_bp.route('/add', methods=['POST'])
def handle_class_add():
    try:
        data = request.get_json()

        name = data.get("name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        now = datetime.now()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO semester_class 
                (name, start_date, end_date, enable, create_date, update_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, start_date, end_date, 0, now, now))

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@class_bp.route('/<int:id>/enable', methods=['POST'])
def handle_class_enable(id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE semester_class
                SET enable = CASE WHEN id = ? THEN 1 ELSE 0 END
            """, (id,))

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@class_bp.route('/<int:semester_class_id>/item', methods=['GET'])
def handle_class_item(semester_class_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, semester_class_id, name, week, slot, type, create_date, update_date
                FROM semester_class_item
                WHERE semester_class_id = ?
                ORDER BY week ASC, slot ASC
            """, (semester_class_id,))
            rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "name": row[2],
                "week": row[3],
                "slot": row[4],
                "type": row[5],
                "create_date": row[6],
                "update_date": row[7]
            })

        return jsonify(items)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@class_bp.route('/<int:semester_class_id>/item/add', methods=['POST'])
def handle_class_item_add(semester_class_id):
    try:
        data = request.get_json()

        name = data.get("name")
        week = data.get("week")
        slot = data.get("slot")
        type_ = data.get("type")
        now = datetime.now()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO semester_class_item
                    (semester_class_id, name, week, slot, type, create_date, update_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (semester_class_id, name, week, slot, type_, now, now))

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@class_bp.route('/<int:semester_class_id>/item/<int:item_id>/delete', methods=['POST'])
def handle_class_item_delete(semester_class_id, item_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    DELETE FROM semester_class_item WHERE semester_class_id = ? AND id = ?
                """, (semester_class_id, item_id))

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
