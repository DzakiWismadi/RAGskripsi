import sys
import os
os.chdir(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV2')

content = open(r'app\app.py', encoding='utf-8').read()

# Find INDEX_HTML and title
idx = content.find('INDEX_HTML =')
title_idx = content.find('<title>', idx)
end_title = content.find('</title>', title_idx)
print(f'V2 Title in app.py: {content[title_idx+7:end_title]}')

# Find /v2 route
idx2 = content.find('@app.get("/v2")')
print(f'"/v2" route found at position: {idx2}')
if idx2 > 0:
    print(f'Next 100 chars: {content[idx2:idx2+100]}')

# Find @app.get("/")
idx3 = content.find('@app.get("/")')
print(f'"/" route found at position: {idx3}')
if idx3 > 0:
    print(f'Next 100 chars: {content[idx3:idx3+100]}')
