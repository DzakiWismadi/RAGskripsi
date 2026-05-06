from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime

# Get the parent directory (QueryDashboard)
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'templates'),
            static_folder=os.path.join(basedir, 'static'))

# Use absolute path for database
db_path = os.path.join(basedir, 'queries.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class QueryTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    queries = db.relationship('Query', backref='table', lazy=True, cascade='all, delete-orphan')

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String(50), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    ground_truth = db.Column(db.Text)
    table_id = db.Column(db.Integer, db.ForeignKey('query_table.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    tables = QueryTable.query.all()
    return render_template('index.html', tables=tables)

@app.route('/table/<int:table_id>')
def view_table(table_id):
    table = QueryTable.query.get_or_404(table_id)
    queries = Query.query.filter_by(table_id=table_id).all()
    for query in queries:
        query.ground_truth_ranked = json.loads(query.ground_truth) if query.ground_truth else []
    return render_template('table.html', table=table, queries=queries)

@app.route('/api/tables', methods=['GET', 'POST'])
def handle_tables():
    if request.method == 'POST':
        data = request.json
        new_table = QueryTable(name=data['name'], description=data.get('description', ''))
        db.session.add(new_table)
        db.session.commit()
        return jsonify({'id': new_table.id, 'name': new_table.name})
    
    tables = QueryTable.query.all()
    return jsonify([{'id': t.id, 'name': t.name, 'description': t.description} for t in tables])

@app.route('/api/tables/<int:table_id>', methods=['DELETE'])
def delete_table(table_id):
    table = QueryTable.query.get_or_404(table_id)
    db.session.delete(table)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/queries/<int:table_id>', methods=['GET', 'POST'])
def handle_queries(table_id):
    if request.method == 'POST':
        data = request.json
        ground_truth_list = data.get('ground_truth_ranked', [])
        new_query = Query(
            query_id=data['query_id'],
            query_text=data['query'],
            ground_truth=json.dumps(ground_truth_list, ensure_ascii=False),
            table_id=table_id
        )
        db.session.add(new_query)
        db.session.commit()
        return jsonify({'id': new_query.id})
    
    queries = Query.query.filter_by(table_id=table_id).all()
    return jsonify([{
        'id': q.id,
        'query_id': q.query_id,
        'query': q.query_text,
        'ground_truth_ranked': json.loads(q.ground_truth) if q.ground_truth else []
    } for q in queries])

@app.route('/api/queries/<int:query_id>', methods=['PUT', 'DELETE'])
def handle_query(query_id):
    query = Query.query.get_or_404(query_id)
    
    if request.method == 'PUT':
        data = request.json
        query.query_id = data['query_id']
        query.query_text = data['query']
        query.ground_truth = json.dumps(data.get('ground_truth_ranked', []), ensure_ascii=False)
        db.session.commit()
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        db.session.delete(query)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/export/<int:table_id>')
def export_json(table_id):
    queries = Query.query.filter_by(table_id=table_id).all()
    data = [{
        'id': q.id,
        'query_id': q.query_id,
        'query': q.query_text,
        'ground_truth_ranked': json.loads(q.ground_truth) if q.ground_truth else []
    } for q in queries]
    
    # Check if this is an AJAX request for copy/paste
    if request.headers.get('Accept') == 'application/json':
        return jsonify(data)
    
    # Use temporary file in the correct directory
    import tempfile
    import os
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f'query_export_{table_id}.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return send_file(filename, as_attachment=True, download_name=f'table_{table_id}_queries.json')

@app.route('/api/import/<int:table_id>', methods=['POST'])
def import_json(table_id):
    file = request.files['file']
    if file and file.filename.endswith('.json'):
        try:
            # Read file content
            content = file.read().decode('utf-8')
            data = json.loads(content)
            count = 0
            for item in data:
                # Check if query_id already exists
                existing = Query.query.filter_by(query_id=item['query_id'], table_id=table_id).first()
                if existing:
                    # Update existing query
                    existing.query_text = item['query']
                    existing.ground_truth = json.dumps(item.get('ground_truth_ranked', []), ensure_ascii=False)
                else:
                    # Create new query
                    new_query = Query(
                        query_id=item['query_id'],
                        query_text=item['query'],
                        ground_truth=json.dumps(item.get('ground_truth_ranked', []), ensure_ascii=False),
                        table_id=table_id
                    )
                    db.session.add(new_query)
                count += 1
            db.session.commit()
            return jsonify({'imported': count, 'updated': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Import failed: {str(e)}'}), 500
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/api/export_selected', methods=['POST'])
def export_selected():
    data = request.json
    query_ids = data.get('query_ids', [])
    
    queries = Query.query.filter(Query.id.in_(query_ids)).all()
    export_data = [{
        'query_id': q.query_id,
        'query': q.query_text,
        'ground_truth_ranked': json.loads(q.ground_truth) if q.ground_truth else []
    } for q in queries]
    
    # Use temporary file
    import tempfile
    import os
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, 'selected_queries.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)