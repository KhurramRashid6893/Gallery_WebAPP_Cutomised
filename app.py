from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for, session
import os
import shutil
import time
import json
from werkzeug.utils import secure_filename
from PIL import Image  # Requires: pip install Pillow

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRASH_DIR = os.path.join(BASE_DIR, 'trash_bin')
TRASH_MAP_FILE = os.path.join(TRASH_DIR, 'map.json')
MEDIA_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm", ".mov")

# Ensure trash directory exists
if not os.path.exists(TRASH_DIR):
    os.makedirs(TRASH_DIR)
if not os.path.exists(TRASH_MAP_FILE):
    with open(TRASH_MAP_FILE, 'w') as f:
        json.dump({}, f)

def get_trash_map():
    try:
        with open(TRASH_MAP_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_trash_map(data):
    with open(TRASH_MAP_FILE, 'w') as f:
        json.dump(data, f)

def get_file_info(full_path, rel_path):
    stats = os.stat(full_path)
    return {
        'name': os.path.basename(full_path),
        'path': rel_path,
        'size': stats.st_size,
        'mtime': stats.st_mtime,
        'type': 'video' if full_path.lower().endswith(('.mp4', '.webm', '.mov')) else 'image'
    }

def get_files_in_folder(folder_path, sort_by='name'):
    files_data = []
    if os.path.exists(folder_path):
        for f in os.listdir(folder_path):
            if f.lower().endswith(MEDIA_EXT):
                full_path = os.path.join(folder_path, f)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                files_data.append(get_file_info(full_path, rel_path))
    
    if sort_by == 'date_desc':
        files_data.sort(key=lambda x: x['mtime'], reverse=True)
    elif sort_by == 'date_asc':
        files_data.sort(key=lambda x: x['mtime'])
    elif sort_by == 'size_desc':
        files_data.sort(key=lambda x: x['size'], reverse=True)
    elif sort_by == 'size_asc':
        files_data.sort(key=lambda x: x['size'])
    else:
        files_data.sort(key=lambda x: x['name'])
        
    return files_data

def get_structure():
    folders = []
    for root, dirs, files in os.walk(BASE_DIR):
        if "templates" in root or "static" in root or "trash_bin" in root or ".__" in root:
            continue
        rel = os.path.relpath(root, BASE_DIR)
        if rel == ".": rel = "Root"
        folders.append(rel)
    return sorted(folders)

# --- ROUTES ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == "admin":
            session['logged_in'] = True
            return redirect("/")
        else:
            return render_template("login.html", error="Wrong Password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect("/login")

@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect("/login")

    folder_param = request.args.get("folder", "Root")
    sort_by = request.args.get("sort", "name")
    view_mode = request.args.get("view", "grid")

    folders = get_structure()
    
    if view_mode == 'trash':
        files_data = []
        trash_map = get_trash_map()
        for stored_name, original_path in trash_map.items():
            full_path = os.path.join(TRASH_DIR, stored_name)
            if os.path.exists(full_path):
                files_data.append(get_file_info(full_path, stored_name))
    else:
        target_dir = BASE_DIR if folder_param == "Root" else os.path.join(BASE_DIR, folder_param)
        files_data = get_files_in_folder(target_dir, sort_by)

    return render_template(
        "index.html",
        folders=folders,
        selected_folder=folder_param,
        files=files_data,
        sort_by=sort_by,
        view_mode=view_mode
    )

@app.route("/media/<path:path>")
def media(path):
    if not session.get('logged_in'): return "Unauthorized", 403
    return send_from_directory(BASE_DIR, path)

@app.route("/trash_media/<path:filename>")
def trash_media(filename):
    if not session.get('logged_in'): return "Unauthorized", 403
    return send_from_directory(TRASH_DIR, filename)

@app.route("/upload", methods=["POST"])
def upload_files():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 403
    
    target_folder = request.form.get('folder', 'Root')
    uploaded_files = request.files.getlist('files[]')
    
    base_upload_path = BASE_DIR if target_folder == 'Root' else os.path.join(BASE_DIR, target_folder)

    if not os.path.exists(base_upload_path):
        os.makedirs(base_upload_path)

    count = 0
    for file in uploaded_files:
        if file and file.filename:
            clean_name = secure_filename(os.path.basename(file.filename))
            save_path = os.path.join(base_upload_path, clean_name)
            file.save(save_path)
            count += 1
            
    return jsonify({"status": "success", "count": count})

@app.route("/rotate", methods=["POST"])
def rotate_image():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    rel_path = data.get("file")
    view_mode = data.get("view_mode", "grid")
    
    if view_mode == 'trash':
        full_path = os.path.join(TRASH_DIR, rel_path) # rel_path is filename in trash
    else:
        full_path = os.path.join(BASE_DIR, rel_path)
    
    try:
        # Open image, rotate -90 (90 degrees clockwise), and save
        with Image.open(full_path) as img:
            rotated = img.rotate(-90, expand=True)
            rotated.save(full_path)
            
        # Return new URL with timestamp to bust cache
        if view_mode == 'trash':
             new_url = f"/trash_media/{rel_path}?t={int(time.time())}"
        else:
             new_url = f"/media/{rel_path}?t={int(time.time())}"
             
        return jsonify({"status": "rotated", "new_url": new_url})
        
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to rotate. Is it an image?"}), 500

@app.route("/delete", methods=["POST"])
def delete_files():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    files_to_delete = data.get("files", [])
    trash_map = get_trash_map()
    
    for rel_path in files_to_delete:
        full_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(full_path):
            timestamp = int(time.time())
            filename = os.path.basename(rel_path)
            trash_name = f"{timestamp}_{filename}"
            
            shutil.move(full_path, os.path.join(TRASH_DIR, trash_name))
            trash_map[trash_name] = rel_path
            
    save_trash_map(trash_map)
    return jsonify({"status": "moved_to_trash"})

@app.route("/restore", methods=["POST"])
def restore_files():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    files_to_restore = data.get("files", [])
    trash_map = get_trash_map()
    
    for trash_name in files_to_restore:
        trash_path = os.path.join(TRASH_DIR, trash_name)
        original_rel_path = trash_map.get(trash_name)
        
        if os.path.exists(trash_path) and original_rel_path:
            dest_path = os.path.join(BASE_DIR, original_rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(trash_path, dest_path)
            del trash_map[trash_name]
            
    save_trash_map(trash_map)
    return jsonify({"status": "restored"})

@app.route("/permanent_delete", methods=["POST"])
def permanent_delete():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    files_to_burn = data.get("files", [])
    trash_map = get_trash_map()
    
    for trash_name in files_to_burn:
        trash_path = os.path.join(TRASH_DIR, trash_name)
        if os.path.exists(trash_path):
            os.remove(trash_path)
        if trash_name in trash_map:
            del trash_map[trash_name]
            
    save_trash_map(trash_map)
    return jsonify({"status": "deleted_forever"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)