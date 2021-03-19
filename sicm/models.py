from sicm import db
from datetime import datetime
from flask_login import UserMixin
from sicm import login_manager


@login_manager.user_loader
def load_user(username):
    return Admin.query.get(username)

class Employee(db.Model):
    matricule = db.Column(db.String(200), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)

    activties = db.relationship('Activity', backref='employee', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name}>"


    @property
    def full_name(self):
        return " ".join((self.first_name.capitalize(), self.last_name.upper()))

    def json(self, with_activities=False):
        data = {
            'matricule': self.matricule,
            'prenom': self.first_name,
            'nom': self.last_name,
            'dates_d\'ajout': self.created_on.date(),
        }
        if with_activities:
            data['activities'] = [i.json() for i in self.activties]

        return data


class Terminal(db.Model):
    matricule = db.Column(db.String(10), primary_key=True)
    location = db.Column(db.String(35))    
    created_on = db.Column(db.DateTime, default=datetime.now)
    
    activties = db.relationship('Activity', backref='terminal', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Terminal {self.matricule}>"
        
    def json(self, with_activities=False):
        data = {
            'matricule': self.matricule,
            'emplacement': self.location,
            'dates_d\'ajout': self.created_on.date(),
        }
        if with_activities:
            data['activities'] = [i.json() for i in self.activties]

        return data


class Admin(db.Model, UserMixin):
    username = db.Column(db.String(25), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        return f"<Administrator {self.username}>"
        
    def get_id(self):
        return self.username


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Integer, default=1)

    employee_matricule = db.Column(db.String(200), db.ForeignKey('employee.matricule'), nullable=False)
    terminal_matricule = db.Column(db.String(10), db.ForeignKey('terminal.matricule'), nullable=False)

    def __repr__(self):
        return f"<Activity {self.id}>"

    def json(self):
        return {
            'id': self.id, 
            'matricule': self.employee_matricule,
            'prenom': self.employee.first_name,
            'nom': self.employee.last_name,
            'emplacement': self.terminal.location,
            'statut': 'entre' if self.status == 0 else 'sorti',
            'date': str(self.date.date()),
            'heur': self.date.strftime('%H:%M:%S')
        }
