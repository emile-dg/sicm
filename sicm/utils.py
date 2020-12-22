from sicm.models import db, Employee, Terminal, Activity

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

def add_new_activity(t_matricule, e_matricule, status):
    activity = Activity(status=status, employee_matricule=e_matricule, terminal_matricule=t_matricule)
    db.session.add(activity)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return "Internal error, database not up to date", 500
    else:
        return "Database updated", 200