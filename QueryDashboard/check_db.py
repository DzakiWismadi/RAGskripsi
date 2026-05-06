import sys
sys.path.insert(0, '.')

from backend.app import Query, QueryTable, db, app

with app.app_context():
    queries = Query.query.all()
    print(f'Total queries: {len(queries)}')
    for q in queries[:5]:
        print(f'ID: {q.query_id}, GT: {q.ground_truth}')
