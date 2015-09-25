import os
import datetime

from flask.ext.sqlalchemy import SQLAlchemy

STATE_PENDING = 1
STATE_RUNNING = 2
STATE_REJECTED = 3
STATE_COMPLETE = 4
STATE_ACCEPTED = 5

TYPE_BUILD = 1
TYPE_FIREWALL = 2

DATABASE_PATH = 'changes.db'

db = SQLAlchemy()

class MetricsState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<MetricsState %r>' % self.description
    
class Metrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    state_id = db.Column(db.Integer, db.ForeignKey('metrics_state.id'))
    state = db.relationship('MetricsState')

    test = db.Column(db.Integer)
    maintainability = db.Column(db.Integer)
    security = db.Column(db.Integer)
    workmanship = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Metrics %r>' % self.id
    
class BuildState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<BuildState %r>' % self.description
    
class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    state_id = db.Column(db.Integer, db.ForeignKey('build_state.id'))
    state = db.relationship('BuildState')

    date = db.Column(db.DateTime)
    
    def __repr__(self):
        return '<Build %r>' % self.id
    
class UnitState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<UnitState %r>' % self.description
    
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)
    
    state_id = db.Column(db.Integer, db.ForeignKey('unit_state.id'))
    state = db.relationship('UnitState')

    chart = db.Column(db.String(80))
    percent = db.Column(db.Integer)
    covered = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Unit %r>' % self.description
    
class FunctionalState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<FunctionalState %r>' % self.description
    
class Functional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)
    
    state_id = db.Column(db.Integer, db.ForeignKey('functional_state.id'))
    state = db.relationship('FunctionalState')
    
    chart = db.Column(db.String(80))
    percent = db.Column(db.Integer)
    covered = db.Column(db.Integer)

    def __repr__(self):
        return '<Functional %r>' % self.description
    
class ChangeType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<ChangeType %r>' % self.description
    
class ChangeState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<ChangeState %r>' % self.description
    
class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=True)
    owner = db.Column(db.String(80))

    type_id = db.Column(db.Integer, db.ForeignKey('change_type.id'))
    type = db.relationship('ChangeType')

    state_id = db.Column(db.Integer, db.ForeignKey('change_state.id'))
    state = db.relationship('ChangeState')

    date = db.Column(db.DateTime)

    metrics_id = db.Column(db.Integer, db.ForeignKey('metrics.id'))
    metrics = db.relationship('Metrics')

    build_id = db.Column(db.Integer, db.ForeignKey('build.id'))
    build = db.relationship('Build')
    
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit')
    
    functional_id = db.Column(db.Integer, db.ForeignKey('functional.id'))
    functional = db.relationship('Functional')

    result_msg = db.Column(db.String(80))
    result_action = db.Column(db.String(80))

    def __repr__(self):
        return '<Change %r>' % self.description

def get_build(change):
    r = {}
    
    if change.build.state:
        r['state'] = change.build.state.description

    if change.build.date:
        r['date'] = str(change.build.date)

    return r
        
def get_metrics(change):
    r = {}
    
    if change.metrics.test:
        r['test'] = change.metrics.test
    
    if change.metrics.maintainability:
        r['maintainability'] = change.metrics.maintainability
    
    if change.metrics.security:
        r['security'] = change.metrics.security
    
    if change.metrics.workmanship:
        r['workmanship'] = change.metrics.workmanship
    
    if change.metrics.state:
        r['state'] = change.metrics.state.description

    return r
        
def get_unit(change):
    r = {}
    
    if change.unit.chart:
        r['chart'] = change.unit.chart
    
    if change.unit.percent:
        r['percent'] = change.unit.percent
    
    if change.unit.covered:
        r['covered'] = change.unit.covered
    
    if change.unit.state:
        r['state'] = change.unit.state.description
    
    return r

def get_functional(change):
    r = {}
    
    if change.functional.chart:
        r['chart'] = change.functional.chart
    
    if change.functional.percent:
        r['percent'] = change.functional.percent
    
    if change.functional.covered:
        r['covered'] = change.functional.covered

    if change.functional.state:
        r['state'] = change.functional.state.description
        
    return r

def get_change_list():
    list = []
    
    changes = Change.query.all()
    for change in changes:
        item = {
            'description': change.description,
            'owner': change.owner,
            'type': change.type.description,
            'state': change.state.description,
            'metrics': get_metrics(change),
            'build': get_build(change),
            'unit': get_unit(change),
            'functional': get_functional(change)
        }

        if change.date:
            item['date'] = str(change.date)
        
        if change.result_msg and change.result_action:
            item['result'] = {
                "message": change.result_msg,
                "button": change.result_action
            }
            
        list.append(item)
        

    return { "changelist": list }
            
def add_common_state(state_class):
    state = state_class()
    state.description = "pending"
    db.session.add(state)
    
    state = state_class()
    state.description = "running"
    db.session.add(state)
    
    state = state_class()
    state.description = "rejected"
    db.session.add(state)

    state = state_class()
    state.description = "complete"
    db.session.add(state)

    state = state_class()
    state.description = "accepted"
    db.session.add(state)
    

def db_create():
    if not os.path.exists(DATABASE_PATH):
        db.create_all()

        add_common_state(MetricsState)
        add_common_state(BuildState)
        add_common_state(UnitState)
        add_common_state(FunctionalState)
        add_common_state(ChangeState)
        
        change_type = ChangeType()
        change_type.description = 'build'
        db.session.add(change_type)
        
        change_type = ChangeType()
        change_type.description = 'firewall'
        db.session.add(change_type)
        
        change = Change()
        change.description = 'Tenrox-R1_1235'
        change.type_id = TYPE_BUILD
        change.state_id = STATE_PENDING
        change.owner = ''
        change.unit = Unit()
        change.unit.state_id = STATE_PENDING
        change.functional = Functional()
        change.functional.state_id = STATE_PENDING
        change.metrics = Metrics()
        change.metrics.state_id = STATE_PENDING
        change.build = Build()
        change.build.state_id = STATE_PENDING
        db.session.add(change)

        change = Change()
        change.description = '432462'
        change.date = datetime.datetime.strptime("4/18/2014 12:12pm", "%m/%d/%Y %I:%M%p")
        change.type_id = TYPE_FIREWALL
        change.state_id = STATE_RUNNING
        change.owner = 'jtuck'
        change.unit = Unit()
        change.unit.state_id = STATE_PENDING
        change.functional = Functional()
        change.functional.state_id = STATE_PENDING
        change.metrics = Metrics()
        change.metrics.state_id = STATE_RUNNING
        change.build = Build()
        change.build.state_id = STATE_PENDING
        db.session.add(change)

        change = Change()
        change.description = '432461'
        change.date = datetime.datetime.strptime("4/18/2014 10:53am", "%m/%d/%Y %I:%M%p")
        change.type_id = TYPE_FIREWALL
        change.state_id = STATE_REJECTED
        change.owner = 'samy'
        change.unit = Unit()
        change.unit.percent = 73
        change.unit.covered = 76
        change.unit.chart = 'chart-unit.png'
        change.unit.state_id = STATE_ACCEPTED
        change.functional = Functional()
        change.functional.percent = 73
        change.functional.covered = 76
        change.functional.chart = 'chart-functional.png'
        change.functional.state_id = STATE_ACCEPTED
        change.metrics = Metrics()
        change.metrics.test = 64
        change.metrics.maintainability = 53
        change.metrics.security = 64
        change.metrics.workmanship = 72
        change.metrics.state_id = STATE_REJECTED
        change.build = Build()
        change.build.state_id = STATE_ACCEPTED
        change.build.date = datetime.datetime.strptime("4/17/2014 10:46am", "%m/%d/%Y %I:%M%p")
        change.result_msg = 'Metrics Reduction'
        change.result_action = 'Find Issues'
        db.session.add(change)

        change = Change()
        change.date = datetime.datetime.strptime("4/17/2014 9:42am", "%m/%d/%Y %I:%M%p")
        change.description = 'Tenrox-R1_1234'
        change.type_id = TYPE_BUILD
        change.state_id = STATE_COMPLETE
        change.owner = ''
        change.unit = Unit()
        change.unit.state_id = STATE_COMPLETE
        change.unit.percent = 73
        change.unit.covered = 76
        change.unit.chart = 'chart-unit.png'
        change.functional = Functional()
        change.functional.state_id = STATE_COMPLETE
        change.functional.percent = 73
        change.functional.covered = 76
        change.functional.chart = 'chart-functional.png'
        change.metrics = Metrics()
        change.metrics.state_id = STATE_COMPLETE
        change.metrics.test = 64
        change.metrics.maintainability = 53
        change.metrics.security = 64
        change.metrics.workmanship = 72
        change.build = Build()
        change.build.state_id = STATE_COMPLETE
        change.build.date = datetime.datetime.strptime("4/17/2014 10:46am", "%m/%d/%Y %I:%M%p")
        db.session.add(change)

        change = Change()
        change.date = datetime.datetime.strptime("4/17/2014 7:51am", "%m/%d/%Y %I:%M%p")
        change.description = '432460'
        change.type_id = TYPE_FIREWALL
        change.state_id = STATE_REJECTED
        change.owner = 'samy'
        change.unit = Unit()
        change.unit.state_id = STATE_PENDING
        change.functional = Functional()
        change.functional.state_id = STATE_PENDING
        change.metrics = Metrics()
        change.metrics.state_id = STATE_REJECTED
        change.metrics.test = 64
        change.metrics.maintainability = 53
        change.metrics.security = 64
        change.metrics.workmanship = 72
        change.build = Build()
        change.build.state_id = STATE_PENDING
        change.result_msg = 'Metrics Reduction'
        change.result_action = 'Find Issues'
        db.session.add(change)

        change = Change()
        change.date = datetime.datetime.strptime("4/16/2014 6:43am", "%m/%d/%Y %I:%M%p")
        change.description = '432459'
        change.type_id = TYPE_FIREWALL
        change.state_id = STATE_ACCEPTED
        change.owner = 'samy'
        change.unit = Unit()
        change.unit.state_id = STATE_ACCEPTED
        change.unit.chart = 'chart-unit.png'
        change.functional = Functional()
        change.functional.state_id = STATE_ACCEPTED
        change.functional.percent = 73
        change.functional.covered = 76
        change.functional.chart = 'chart-functional.png'
        change.metrics = Metrics()
        change.metrics.state_id = STATE_REJECTED
        change.metrics.test = 64
        change.metrics.maintainability = 53
        change.metrics.security = 64
        change.metrics.workmanship = 72
        change.metrics.state_id = STATE_ACCEPTED
        change.build = Build()
        change.build.state_id = STATE_ACCEPTED
        change.build.date = datetime.datetime.strptime("4/16/2014 6:43am", "%m/%d/%Y %I:%M%p")
        change.unit.percent = 73
        change.unit.covered = 76
        change.result_msg = 'Auto-Merged'
        change.result_action = 'Merged Build'
        db.session.add(change)

        change = Change()
        change.date = datetime.datetime.strptime("4/17/2014 6:43am", "%m/%d/%Y %I:%M%p")
        change.description = '432458'
        change.type_id = TYPE_FIREWALL
        change.state_id = STATE_ACCEPTED
        change.owner = 'samy'
        change.unit = Unit()
        change.unit.state_id = STATE_ACCEPTED
        change.unit.chart = 'chart-unit.png'
        change.functional = Functional()
        change.functional.state_id = STATE_ACCEPTED
        change.functional.percent = 73
        change.functional.covered = 76
        change.functional.chart = 'chart-functional.png'
        change.metrics = Metrics()
        change.metrics.state_id = STATE_REJECTED
        change.metrics.test = 64
        change.metrics.maintainability = 53
        change.metrics.security = 64
        change.metrics.workmanship = 72
        change.metrics.state_id = STATE_ACCEPTED
        change.build = Build()
        change.build.state_id = STATE_ACCEPTED
        change.build.date = datetime.datetime.strptime("4/16/2014 6:43am", "%m/%d/%Y %I:%M%p")
        change.unit.percent = 73
        change.unit.covered = 76
        change.result_msg = 'Auto-Merged'
        change.result_action = 'Merged Build'
        db.session.add(change)
		
        db.session.commit()
        
