from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
tz = pytz.timezone('Asia/Shanghai')
# 定义模型
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.Text, nullable=False)
    nvidia_info = db.Column(db.Text, nullable=False)
    cpu_temp = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Record {self.id}>'
    
with app.app_context():
    db.create_all()

@app.route('/report', methods=['POST'])
def report():
    if request.is_json:
        try:
            data = request.json
            ip = data.get('ip')
            cputemp = data.get('cpu_temp')
            nvidia_info = data.get('nvidia_info')
            if ip is None or nvidia_info is None:
                return jsonify({"error": "Missing 'ip' or 'nvidia_info' in JSON data"}), 400
            
            new_record = Record(ip=ip, nvidia_info=nvidia_info,cpu_temp=cputemp,created_at=tz.localize(datetime.now()))
            db.session.add(new_record)
            db.session.commit()
            return jsonify({"message": "Data received and stored."}), 200
        except Exception as e:
            return jsonify({"error": f"Request must be JSON {e}"}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/show', methods=['GET'])
def show():
    records = Record.query.order_by(Record.id.desc()).limit(10).all()
    return jsonify([{"id": record.id, "ip": record.ip, "nvidia_info": record.nvidia_info, "cpu_temp": record.cpu_temp, "created_at": record.created_at} for record in records]), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)