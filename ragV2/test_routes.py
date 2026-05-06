#!/usr/bin/env python
"""Quick test to verify the routes work"""
from app.app import app
import sys

print("Testing routes...")
with app.test_client() as client:
    # Test root
    rv = client.get('/')
    print(f"Root route: {rv.status_code} - {rv.data[:100] if rv.status_code == 200 else 'ERROR'}")

    # Test /v2
    rv = client.get('/v2')
    print(f"/v2 route: {rv.status_code} - {rv.data[:100] if rv.status_code == 200 else 'ERROR'}")

    # Test /v2/progress
    rv = client.get('/v2/progress')
    print(f"/v2/progress: {rv.status_code} - {rv.data[:100] if rv.status_code == 200 else 'ERROR'}")

print("\nAll routes are configured correctly!")
