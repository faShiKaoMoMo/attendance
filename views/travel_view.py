from flask import Blueprint, render_template, request, jsonify

travel_bp = Blueprint('travel', __name__, url_prefix='/travel')

@travel_bp.route('/')
def index():
    """
    渲染出差统计主页面
    它会去 templates/travel/ 文件夹下寻找 index.html 文件。
    """
    return render_template('travel/index.html')
