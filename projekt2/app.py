import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import requests
import hashlib
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

API_KEY = 'YnTXJnvAqwfy1686'
SECRET_KEY = 'ff266dac57a04b2d9e9d07affc3aa8e7'
BASE_URL = 'https://www.kd100.com/api/v1/tracking/realtime'

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier_id = db.Column(db.String(50), nullable=False)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(100), nullable=False, default="Nieznany")
    custom_name = db.Column(db.String(100), nullable=True) 

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    packages = Package.query.all()
    return render_template('index.html', packages=packages)

def track_package(carrier_id, tracking_number):
    params = {
        "carrier_id": carrier_id,
        "tracking_number": tracking_number,
        "area_show": 1,
        "order": "desc",
        "phone": "",
        "ship_from": "",
        "ship_to": ""
    }
    
    param_str = json.dumps(params, indent=4)
    temp_sign = param_str + API_KEY + SECRET_KEY
    md = hashlib.md5()
    md.update(temp_sign.encode())
    signature = md.hexdigest().upper()

    headers = {
        "API-Key": API_KEY,
        "signature": signature,
        "Content-Type": "application/json; charset=utf-8"
    }

    logging.info(f"🚀 Wysyłamy zapytanie do API KD100: \nHeaders: {headers}\nPayload: {param_str}")
    response = requests.post(BASE_URL, headers=headers, data=param_str)

    logging.info(f"🔍 API Response for {tracking_number}: {response.text}")

    if response.status_code == 200:
        data = response.json()
        return data.get('data', None)
    else:
        logging.error(f"❌ API Error {response.status_code}: {response.text}")
        return None

@app.route('/track_or_add', methods=['POST'])
def track_or_add():
    carrier_id = request.form['carrier_id']
    tracking_number = request.form['tracking_number'].strip()  
    action = request.form['action']

    if not tracking_number:  
        return render_template('error.html', message="Numer śledzenia nie może być pusty.")

    package = Package.query.filter_by(tracking_number=tracking_number).first()

    if action == "track":
        tracking_info = track_package(carrier_id, tracking_number)
        if tracking_info:
            return render_template('tracking_info.html', tracking_info=tracking_info)
        else:
            return render_template('error.html', message="Nie znaleziono danych o paczce.")

    elif action == "add":
        if package:
            return render_template('error.html', message="Paczka już istnieje w bazie.")

        tracking_info = track_package(carrier_id, tracking_number)

        if not tracking_info or 'items' not in tracking_info or not tracking_info['items']:  
            return render_template('error.html', message="Paczka o podanym numerze nie istnieje.")

        latest_status = tracking_info['items'][0].get('order_status_description', "Nieznany")

        logging.info(f"🛠️ Zapisujemy paczkę {tracking_number} ze statusem: {latest_status}")

        new_package = Package(
            carrier_id=carrier_id,
            tracking_number=tracking_number,
            status=latest_status,
            custom_name=None  
        )
        db.session.add(new_package)
        db.session.commit()
        return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/edit/<int:package_id>', methods=['GET', 'POST'])
def edit_package(package_id):
    package = Package.query.get_or_404(package_id)

    if request.method == 'POST':
        package.custom_name = request.form['custom_name']  
        db.session.commit()
        logging.info(f"✏️ Zaktualizowano nazwę paczki {package.tracking_number}")
        return redirect(url_for('index'))

    return render_template('edit.html', package=package)

@app.route('/delete/<int:package_id>', methods=['POST'])
def delete_package(package_id):
    try:
        package = Package.query.get_or_404(package_id)
        db.session.delete(package)
        db.session.commit()
        logging.info(f"🗑️ Usunięto paczkę {package.tracking_number}")
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"❌ Błąd podczas usuwania paczki: {str(e)}")
        return render_template('error.html', message="Wystąpił błąd podczas usuwania paczki.")

class PackageAPI(Resource):
    def get(self, tracking_number):
        package = Package.query.filter_by(tracking_number=tracking_number).first()
        if package:
            return {
                'carrier_id': package.carrier_id,
                'tracking_number': package.tracking_number,
                'status': package.status,
                'custom_name': package.custom_name
            }, 200
        return {'message': 'Paczka nie znaleziona'}, 404

api.add_resource(PackageAPI, '/api/package/<string:tracking_number>')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)

