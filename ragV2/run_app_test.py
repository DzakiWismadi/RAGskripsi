import sys
import os
os.chdir(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2')

try:
    print("Importing app...")
    exec(open(r'app\app.py', encoding='utf-8').read())
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
