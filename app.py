from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

def get_db_connection():
    conn = sqlite3.connect('employes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Utilisateur actuel : {current_user.username}")
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and user['password'] == password:
            login_user(User(id=user['id'], username=user['username'], password=user['password']))
            print(f"Connexion réussie pour : {username}")
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.')
            print("Échec de la connexion.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    print(f"Déconnexion de l'utilisateur : {current_user.username}")
    logout_user()
    session.clear()
    print("Utilisateur déconnecté et session réinitialisée.")
    return redirect(url_for('login'))

@app.route('/comptabilite')
@login_required
def comptabilite():
    conn = get_db_connection()
    employes = conn.execute('SELECT * FROM employes').fetchall()
    grades = conn.execute('SELECT * FROM grades').fetchall()
    quotas = {grade['grade']: grade['quota'] for grade in grades}
    bonuses = {grade['grade']: grade['bonus'] for grade in grades}
    salaries = {grade['grade']: grade['salaire'] for grade in grades}
    total_payer = sum([emp['salaire'] for emp in employes])
    conn.close()
    return render_template('index.html', employes=employes, quotas=quotas, bonuses=bonuses, salaries=salaries, grades=grades, total_payer=total_payer)

@app.route('/calendrier')
@login_required
def calendrier():
    return render_template('calendrier.html')

@app.route('/absence')
@login_required
def absence():
    return render_template('absence.html')

@app.route('/contrat')
@login_required
def contrat():
    return render_template('contrat.html')

@app.route('/add', methods=['POST'])
@login_required
def add():
    nom = request.form['nom']
    prenom = request.form['prenom']
    grade = request.form['grade']
    nombre_factures = int(request.form['nombre_factures'])
    conn = get_db_connection()
    grade_info = conn.execute('SELECT quota, bonus, salaire FROM grades WHERE grade = ?', (grade,)).fetchone()
    quota = grade_info['quota']
    bonus = grade_info['bonus']
    salaire_base = grade_info['salaire']
    
    salaire_total = salaire_base
    if nombre_factures > quota:
        salaire_total += (nombre_factures - quota) * bonus
    
    conn.execute('INSERT INTO employes (nom, prenom, grade, nombre_factures, salaire) VALUES (?, ?, ?, ?, ?)',
                 (nom, prenom, grade, nombre_factures, salaire_total))
    conn.commit()
    conn.close()
    return redirect(url_for('comptabilite'))

@app.route('/update', methods=['POST'])
@login_required
def update():
    id = int(request.form['id'])
    nombre_factures = int(request.form['nombre_factures'])
    conn = get_db_connection()
    employe = conn.execute('SELECT grade FROM employes WHERE id = ?', (id,)).fetchone()
    grade = employe['grade']
    grade_info = conn.execute('SELECT quota, bonus, salaire FROM grades WHERE grade = ?', (grade,)).fetchone()
    quota = grade_info['quota']
    bonus = grade_info['bonus']
    salaire_base = grade_info['salaire']
    
    salaire_total = salaire_base
    if nombre_factures > quota:
        salaire_total += (nombre_factures - quota) * bonus
    
    conn.execute('UPDATE employes SET nombre_factures = ?, salaire = ? WHERE id = ?', (nombre_factures, salaire_total, id))
    conn.commit()
    conn.close()
    return redirect(url_for('comptabilite'))

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    id = int(request.form['id'])
    conn = get_db_connection()
    conn.execute('DELETE FROM employes WHERE id = ?', (id,))
    conn.commit()

    reset_ids(conn)

    conn.close()
    return redirect(url_for('comptabilite'))

def reset_ids(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS employes_backup AS SELECT * FROM employes')

    conn.execute('DROP TABLE employes')

    conn.execute('''
        CREATE TABLE employes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            grade TEXT NOT NULL,
            nombre_factures INTEGER NOT NULL,
            salaire REAL NOT NULL
        )
    ''')

    conn.execute('''
        INSERT INTO employes (nom, prenom, grade, nombre_factures, salaire)
        SELECT nom, prenom, grade, nombre_factures, salaire FROM employes_backup
    ''')

    conn.execute('DROP TABLE employes_backup')

    conn.commit()

@app.route('/add_grade', methods=['POST'])
@login_required
def add_grade():
    new_grade = request.form['newGrade']
    new_quota = int(request.form['newQuota'])
    new_bonus = float(request.form['newBonus'])
    new_salaire = float(request.form['newSalaire'])
    conn = get_db_connection()
    conn.execute('INSERT INTO grades (grade, quota, bonus, salaire) VALUES (?, ?, ?, ?)', (new_grade, new_quota, new_bonus, new_salaire))
    conn.commit()
    conn.close()
    return redirect(url_for('comptabilite'))

@app.route('/delete_grade', methods=['POST'])
@login_required
def delete_grade():
    grade_to_delete = request.form['gradeToDelete']
    conn = get_db_connection()
    conn.execute('DELETE FROM grades WHERE grade = ?', (grade_to_delete,))
    conn.commit()
    conn.close()
    return redirect(url_for('comptabilite'))

@app.route('/update_quota', methods=['POST'])
@login_required
def update_quota():
    grade = request.form['gradeToUpdate']
    new_quota = int(request.form['newQuota'])
    new_bonus = float(request.form['newBonus'])
    new_salaire = float(request.form['newSalaire'])
    conn = get_db_connection()
    conn.execute('UPDATE grades SET quota = ?, bonus = ?, salaire = ? WHERE grade = ?', (new_quota, new_bonus, new_salaire, grade))
    conn.commit()
    conn.close()
    return redirect(url_for('comptabilite'))

if __name__ == '__main__':
    app.run(debug=True)
