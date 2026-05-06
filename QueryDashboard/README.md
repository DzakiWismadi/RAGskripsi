# Query Dashboard

Simple dashboard for managing and testing ISO 27001 compliance queries.

## Features

- Create multiple query tables (e.g., simple paragraph queries, complex paragraph queries)
- Add, edit, and delete individual queries
- Import/export queries in JSON format
- Select specific queries and export them for testing
- SQLite database for persistent storage

## Installation

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python backend/app.py
```

4. Open browser: http://localhost:5000

## Usage

1. **Create Table**: Click "Create New Table" to add a new query table
2. **Add Queries**: Open a table and add individual queries
3. **Import JSON**: Bulk import queries from JSON file
4. **Export**: Export all or selected queries to JSON for testing

## JSON Format

```json
[
  {
    "query_id": "Q181",
    "query": "Query text here...",
    "ground_truth_ranked": ["A.6.3"]
  }
]
```
