@echo off
cd /d "D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2"
echo Starting Flask server...
echo Please wait 30-60 seconds for models to load...
start "RAG V2 Server" python app\app.py
echo Server started in new window.
echo Wait for the message "Running on http://127.0.0.1:5001"
echo Then open your browser to: http://127.0.0.1:5001/v2
pause