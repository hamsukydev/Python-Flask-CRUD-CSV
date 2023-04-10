from flask import Flask,render_template,request,url_for,redirect,Response
from flask_sqlalchemy import SQLAlchemy
import io
from io import TextIOWrapper
import csv
from sqlalchemy.sql import text

app = Flask(__name__)
app.secret_key = "secret_key"

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Replace 'my_database.db' with your SQLite database file

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Data(db.Model):
    __tablename__ = 'stations'
    id = db.Column(db.String(128), primary_key=True)
    code = db.Column(db.String(128), nullable = False)
    name = db.Column(db.String(128), nullable = False, unique = True)
    stations_type = db.Column(db.String(128), nullable = False)

    def __init__(self,id,code,name,stations_type):
 
        self.id = id
        self.code = code
        self.name = name
        self.stations_type = stations_type

@app.route('/')
def index():
    stations = Data.query.all()
    return render_template('index.html',stations = stations)

@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == "POST":
        id =  request.form['id']
        code =  request.form['code']
        name =  request.form['name']
        stations_type =  request.form['stations_type']
 
        station_data = Data(id, code, name, stations_type)
        db.session.add(station_data)
        db.session.commit()
 
        return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    if request.method == "POST":
        station_data = Data.query.get(int(id))

        station_data.id =  request.form['id']
        station_data.code =  request.form['code']
        station_data.name =  request.form['name']
        station_data.stations_type =  request.form['stations_type']

        db.session.commit()
 
        return redirect(url_for('index'))
 
@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
def delete(id):
    station_data = Data.query.get(id)
    db.session.delete(station_data)
    db.session.commit()

    return redirect(url_for('index'))

@app.route("/upload", methods=['POST'])
def uploadFiles():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            stations = Data(id=row[0], code=row[1], name=row[2], stations_type=row[3])
            db.session.add(stations)
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/csv_report')
def download_csv():
    result = db.session.execute("SELECT id,code,name,stations_type FROM stations")

    output = io.StringIO()
    writer = csv.writer(output)

    for row in result:
        line = [row[0] ,row[1], row[2],row[3]]
        writer.writerow(line)

    output.seek(0)
    db.session.commit()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=transit-station-report.csv"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        app.run(debug=True)