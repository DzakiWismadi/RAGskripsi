#!/usr/bin/env python
import subprocess
import time
import sys

print("Starting Flask server...")
proc = subprocess.Popen(
    [sys.executable, r"app\app.py"],
    cwd=r"D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

print("Waiting for server to start...")
time.sleep(15)  # Give it 15 seconds to load models

# Try to connect
import requests
try:
    r = requests.get('http://127.0.0.1:5001/')
    title = r.text[r.text.find('<title>')+7:r.text.find('</title>')]
    print(f"SUCCESS! Server is running!")
    print(f"Root page title: {title}")

    r2 = requests.get('http://127.0.0.1:5001/v2')
    print(f"/v2 status: {r2.status_code}")
    if r2.status_code == 200:
        title2 = r2.text[r2.text.find('<title>')+7:r2.text.find('</title>')]
        print(f"/v2 page title: {title2}")
    else:
        print(f"/v2 error: {r2.text[:200]}")

except Exception as e:
    print(f"ERROR: Could not connect to server: {e}")

print("\nServer is still running. Press Ctrl+C to stop.")
try:
    proc.wait()
except KeyboardInterrupt:
    print("\nStopping server...")
    proc.terminate()
