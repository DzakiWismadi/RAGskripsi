from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
db_path = os.path.join(basedir, 'queries.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Query(db.Model):
    __tablename__ = 'query'
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String(50), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    ground_truth = db.Column(db.Text)
    table_id = db.Column(db.Integer,)

with app.app_context():
    # Get first query
    first_query = db.session.query(Query).first()
    if first_query:
        print('First query found:')
        print(f'ID: {first_query.id}')
        print(f'Query ID: {first_query.query_id}')
        print(f'Query Text (first 100 chars): {first_query.query_text[:100]}')
        print(f'Ground Truth raw: {repr(first_query.ground_truth)}')
        print(f'Ground Truth parsed: {json.loads(first_query.ground_truth) if first_query.ground_truth else []}')
    else:
        print('No queries found')