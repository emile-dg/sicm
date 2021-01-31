from sicm.models import db, Employee, Terminal, Activity
from datetime import datetime

def verify_employee(matricule):
    if Employee.query.get(matricule):
        return True
    else:
        return False

def verify_terminal(matricule):
    if Terminal.query.get(matricule):
        return True
    else:
        return False

def add_new_activity(t_matricule, e_matricule):
    last_updates = [act for act in Activity.query.filter_by(employee_matricule=e_matricule).all() 
                        if act.date.date()==datetime.now().date()]
    last_update = last_updates[0] if last_updates else None # get the last update for the employee during that day
    if last_update:
        status = 0 if last_update.status == 1 else 1
    else:
        status = 0
    activity = Activity(status=status, employee_matricule=e_matricule, terminal_matricule=t_matricule)
    db.session.add(activity)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return "Internal error, database not up to date", 500
    else:
        return Employee.query.get(e_matricule).full_name, 200