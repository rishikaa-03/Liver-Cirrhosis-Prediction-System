from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'


with open('model.pkl','rb') as f:
    model = pickle.load(f)


conn = sqlite3.connect('patients.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                age INTEGER,
                gender TEXT,
                bilirubin REAL,
                albumin REAL,
                copper REAL,
                alk_phos REAL,
                sgot REAL,
                platelets REAL,
                prothrombin REAL,
                ascites TEXT,
                hepatomegaly TEXT,
                spiders TEXT,
                edema TEXT,
                stage TEXT)''')
conn.commit()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                      (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except:
            return "Username already exists"

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login"

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect('/')

@app.route('/prediction')
def prediction():
    if 'user' in session:
        return render_template('prediction.html')
    else:
        return redirect('/')

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/')

    data = request.form
    
    patient = {
        'patient_name': data['patient_name'],
        'age': int(data['age']),
        'gender': data['gender'],
        'bilirubin': float(data['bilirubin']),
        'albumin': float(data['albumin']),
        'copper': float(data['copper']),
        'alk_phos': float(data['alk_phos']),
        'sgot': float(data['sgot']),
        'platelets': float(data['platelets']),
        'prothrombin': float(data['prothrombin']),
        'ascites': data['ascites'],
        'hepatomegaly': data['hepatomegaly'],
        'spiders': data['spiders'],
        'edema': data['edema']
    }

    
    input_df = pd.DataFrame([[
        patient['age'],
        1 if patient['gender']=='Male' else 0,
        patient['bilirubin'],
        patient['albumin'],
        patient['copper'],
        patient['alk_phos'],
        patient['sgot'],
        patient['platelets'],
        patient['prothrombin'],
        1 if patient['ascites']=='Yes' else 0,
        1 if patient['hepatomegaly']=='Yes' else 0,
        1 if patient['spiders']=='Yes' else 0,
        1 if patient['edema']=='Yes' else 0
    ]], columns=['age','gender','bilirubin','albumin','copper','alk_phos','sgot',
                 'platelets','prothrombin','ascites','hepatomegaly','spiders','edema'])

    stage = model.predict(input_df)[0]

  
    recommendations = {
        '1': 'Maintain healthy diet & regular checkups',
        '2': 'Consult hepatologist & follow treatment plan',
        '3': 'Requires medication & close monitoring',
        '4': 'Advanced care needed, possible hospitalization'
    }
    rec = recommendations.get(str(stage), 'Consult doctor')

    
    c.execute('''INSERT INTO patients 
        (patient_name,age,gender,bilirubin,albumin,copper,alk_phos,sgot,platelets,prothrombin,
        ascites,hepatomegaly,spiders,edema,stage)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (patient['patient_name'],patient['age'],patient['gender'],patient['bilirubin'],
         patient['albumin'],patient['copper'],patient['alk_phos'],patient['sgot'],patient['platelets'],
         patient['prothrombin'],patient['ascites'],patient['hepatomegaly'],patient['spiders'],
         patient['edema'],stage))
    conn.commit()

    return render_template('result.html', stage=stage, recommendation=rec, patient=patient)

if __name__ == '__main__':
    app.run(debug=True)
