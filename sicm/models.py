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


class Terminal(db.Model):
    matricule = db.Column(db.String(10), primary_key=True)
    location = db.Column(db.String(35))    
    created_on = db.Column(db.DateTime, default=datetime.now)
    
    activties = db.relationship('Activity', backref='terminal', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Terminal {self.matricule}>"


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
            'date': self.date,
            'status': 'entre' if self.status == 0 else 'sorti',
            'first_name': self.employee.first_name,
            'last_name': self.employee.last_name,
            'location': self.terminal.location
        }
