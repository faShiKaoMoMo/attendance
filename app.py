from flask import Flask, render_template

from views.class_view import class_bp
from views.attendance_view import attendance_bp
from views.config_view import config_bp
from views.travel_view import travel_bp

app = Flask(__name__)

app.register_blueprint(class_bp)
app.register_blueprint(config_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(travel_bp)

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
