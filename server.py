import os

from flask import Flask, render_template, jsonify, send_from_directory
from models import db, db_create, get_change_list, DATABASE_PATH

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % DATABASE_PATH
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)
    with app.app_context():
        db_create()

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static/img'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')
                                   
    @app.route('/changelist', methods=['POST'])
    def changelist():
        return jsonify(get_change_list())
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()