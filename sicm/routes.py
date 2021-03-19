import json
import os
import time
import sys
from datetime import datetime
from secrets import token_hex

from flask import (abort, flash, redirect, render_template, request, send_file,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from sicm import app, bcrypt, db
from sicm.models import Activity, Admin, Employee, Terminal
from sicm.utils import add_new_activity, verify_employee, verify_terminal


@app.route('/')
@login_required
def home():
    FETCH_LIMIT = 20
    current_date = datetime.now().date()
    data = [i.json() for i in Activity.query.all() if i.date.date() == current_date][:FETCH_LIMIT][::-1]
    details = {
        'employés_enregistrés': Employee.query.count(),
        'terminales_enregistrés': Terminal.query.count(),
        'total_entrées_/_sorties': Activity.query.count(),
    }

    return render_template("sicm/index.html", details=details, page_title="acceuil", data=data, page_index=0)


@app.route('/connecter', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method.upper() == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        remember_user = True if request.form.get('remember')=='on' else False

        if username and password:
            admin = Admin.query.get(username)
            if admin:
                if bcrypt.check_password_hash(admin.password, password):
                    login_user(admin, remember=remember_user)
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
                        flash("Une erreur innatendue s'est produite durant l'operation.", 'danger')
                    else:
                        flash('Employé enregistré dans la base de données', 'success')
                else:
                    flash("Le nom est manquant", 'danger')
            else:
                flash('Le prenom est manquant', 'danger')
        else:
            flash('Le matricule est manquant', 'danger')
    data = [ i.json() for i in Employee.query.all() ]
    return render_template("sicm/employees.html", page_title="employés enregistrés", data=data, page_index=1)

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
            flash("Désolé, l'operation a été annulé suite a une erreur interne", 'danger')
        else:
            flash("Employé retiré de la base de donnée", 'success')
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
                    flash("Une erreur innatendue s'est produite durant l'operation.", 'danger')
                else:
                    flash("Terminale ajouté avec succés.", 'success')
            else:
                flash("La description de l'emplacement du terminale est manquante.", 'danger')
        else:
            flash('Le matricule du terminale est manquant.')
    
    data = [ i.json() for i in Terminal.query.all() ]

    return render_template("sicm/terminals.html", page_title="terminales enregistrés", data=data, page_index=2)

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
            flash("Desolé, l'operation a été annulée suite a une érreur interne", 'danger')
        else:
            flash("Terminale retiré de la base de donnée", 'success')
    else:
        return abort(404)
    return redirect(url_for('terminals'))
    
@app.route('/activites')
@app.route('/activites/<int:status>')
@login_required
def activity_listing(status=-1):
    do_export = request.args.get('export', False)
    raw_date = request.args.get('date', False)
    if raw_date:
        date = datetime.strptime(raw_date, '%Y-%m-%d').date()
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

    if do_export:
        fn = getattr(sys.modules['__main__'], '__file__')
        root_path = os.path.abspath(os.path.dirname(fn))
        filename = os.path.join(root_path, 'sicm', 'temp', f'{time.time()}.json')
        export_file = {'data': data}
        with open(filename, 'w+') as file:
            json.dump(export_file, file)
        return send_file(filename)

    return render_template("sicm/activity_listing.html", page_title=f"liste des activitées", date=date.strftime('%d-%m-%Y'), data=data[::-1], status=status, page_index=3)
  

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
                return add_new_activity(terminal_matrcule, employee_matricule)
            else:
                return "Invalid Employee", 404
        else:
            return "Invalid Terminal", 404
    else:
        return "Missing inputs", 404
