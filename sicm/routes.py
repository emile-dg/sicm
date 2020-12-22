from flask import request, render_template, url_for, redirect, flash, abort
from sicm import app, db, bcrypt
from sicm.utils import verify_employee, verify_terminal, add_new_activity
from sicm.models import Activity, Employee, Terminal, Admin
from datetime import datetime
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
@login_required
def home():
    date = datetime.now().date()
    data = [i.json() for i in Activity.query.limit(10).all() if i.date.date() == date]
    return render_template("sicm/index.html", data=data)


@app.route('/connecter', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method.upper() == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            admin = Admin.query.get(username)
            if admin:
                if bcrypt.check_password_hash(admin.password, password):
                    login_user(admin)
                    return redirect(url_for('home'))
                else:
                    flash("Mot de passe incorrecte", 'danger')
            else:
                flash("Nom d'utilisateur invalide", 'danger')
        else:
            flash('Formulaire manquant', 'danger')
    return render_template('sicm/login.html')


@app.route('/deconnecter')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/employes', methods=['GET', 'POST'])
@login_required
def employees():
    if request.method.upper() == "POST":
        matricule = request.form.get('matricule')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        if matricule:
            if first_name:
                if last_name:
                    employee = Employee(matricule=matricule, first_name=first_name, last_name=last_name)
                    db.session.add(employee)
                    try:
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        flash("Une erreur innatendue s'est produit durant l'operation.", 'danger')
                    else:
                        flash('Employe enregistre dans la base de donnees', 'success')
                else:
                    flash("Le nom est manquant", 'danger')
            else:
                flash('Le prenom est manquant', 'danger')
        else:
            flash('Le matricule est manquant', 'danger')
    data = Employee.query.all()
    return render_template("sicm/employees.html", data=data)

@app.route('/retirer_employe/<string:matricule>')
@login_required
def delete_employee(matricule):
    employee = Employee.query.get(matricule)
    if employee:
        db.session.delete(employee)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("Desole, l'operation a ete annule suite a une erreur interne", 'danger')
        else:
            flash("Employe retire de la base de donnee", 'success')
    else:
        return abort(404)
    return redirect(url_for('employees'))
    
@app.route('/terminals', methods=['GET', 'POST'])
@login_required
def terminals():
    if request.method.upper() == "POST":
        terminal_matricule = request.form.get('matricule')
        terminal_location = request.form.get('location')
        if terminal_matricule:
            if terminal_location:
                terminal = Terminal(matricule=terminal_matricule, location=terminal_location)
                db.session.add(terminal)
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    flash("Une erreur innatendue s'est produit durant l'operation.", 'danger')
                else:
                    flash("Terminale ajoutee avec success.", 'success')
            else:
                flash("La description de l'emplacement du terminale est manquante.", 'danger')
        else:
            flash('Le matricule du terminale est manquant.')
    
    data = Terminal.query.all()

    return render_template("sicm/terminals.html", data=data)

@app.route('/retirer_terminale/<string:matricule>')
@login_required
def delete_terminal(matricule):
    termainal = Terminal.query.get(matricule)
    if termainal:
        db.session.delete(termainal)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("Desole, l'operation a ete annulee suite a une erreur interne", 'danger')
        else:
            flash("Terminale retire de la base de donnee", 'success')
    else:
        return abort(404)
    return redirect(url_for('terminals'))
    
@app.route('/activites', methods=['GET', 'POST'])
@app.route('/activites/<int:status>', methods=['GET', 'POST'])
@login_required
def activity_listing(status=-1):
    if request.method.upper() == "POST":
        raw_date = request.form.get('date')
        if raw_date:
            date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        else:
            date =  datetime.now().date()
    else:
        date =  datetime.now().date()

    if status < -1 and status > 1:
        return abort(404)
    elif status == -1:
        data = [ i.json() for i in \
                Activity.query.order_by(Activity.date.asc()).all() \
                if i.date.date() == date
            ]
    else:
        data = [ i.json() for i in \
                Activity.query.filter_by(status=status).order_by(Activity.date.asc()).all() \
                if i.date.date() == date
            ]

    return render_template("sicm/activity_listing.html", data=data)


@app.route("/verify", methods=['GET','POST'])
def verify():
    if request.method.upper() == "GET":
        return "Invalid method", 404

    terminal_matrcule = request.form.get('terminal_matrcule')
    employee_matricule = request.form.get('employee_matricule')

    if terminal_matrcule and employee_matricule:
        if verify_terminal(terminal_matrcule):
            if verify_employee(employee_matricule):
                return "Valid", 200
            else:
                return "Invalid Employee", 404
        else:
            return "Invalid Terminal", 404
    else:
        return "Missing inputs", 404


@app.route("/add_activity", methods=['POST'])
def add_activity():

    terminal_matrcule = request.form.get('terminal_matricule')
    employee_matricule = request.form.get('employee_matricule')

    if terminal_matrcule and employee_matricule:
        if verify_terminal(terminal_matrcule):
            if verify_employee(employee_matricule):
                status = request.form.get('status')
                if status:
                    return add_new_activity(terminal_matrcule, employee_matricule, status)
                else:
                    return "Missing Status", 404
            else:
                return "Invalid Employee", 404
        else:
            return "Invalid Terminal", 404
    else:
        return "Missing inputs", 404