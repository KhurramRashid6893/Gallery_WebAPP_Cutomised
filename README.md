Here is a **clean, simple, copy-paste ready `README.md`** for your project.
It explains everything **clearly for users**, no technical overload.

---

# 📁 Media Gallery Web App

A simple local **image & video gallery** built with **Flask**.
Browse folders, preview images/videos, filter content, and manage files easily.

---

## 🚀 Features

* 📂 Auto-detects all folders and subfolders
* 🖼️ View images & videos together
* 🔍 Filter by **Images / Videos**
* 🗂 Folder navigation from sidebar
* 🗑 Delete files (with confirmation)
* 🖱 Multi-select support
* 📱 Works on mobile & desktop
* 🔐 Runs locally (no internet needed)

---

## 📁 Project Structure

```
project/
│
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── (your image & video folders)
```

---

## ⚙️ Requirements

* Python 3.8+
* Flask

Install Flask:

```bash
pip install flask
pip install pillow
```

---

## ▶️ How to Run

1. Open terminal in project folder
2. Run the app:

```bash
python app.py
```

3. Open browser and visit:

```
http://127.0.0.1:5000
```

---

## 🧭 How to Use

### 📂 Browse Files

* All folders appear on the **left sidebar**
* Click any folder to view its contents

### 🖼 View Media

* Images and videos load automatically
* Click on items to select them

### 🔎 Filter

* Use **All / Images / Videos** buttons at the top

### 🗑 Delete Files

1. Select one or multiple files
2. Click **Delete**
3. Confirm deletion

> Deleted files are removed from disk (no recycle bin unless you add one).

---

## 📱 Mobile Support

* Tap to select
* Scroll-friendly layout
* Works on phones and tablets

---

## ⚠️ Important Notes

* Do **not** delete system folders (`templates`, `static`)
* App runs locally only (not exposed to internet)
* Files are permanently deleted unless you add trash recovery

---

## 🧩 Optional Enhancements (Future)

* 🔐 Login / password protection
* ♻ Trash restore system
* 🔍 Search bar
* 🗂 Drag & drop upload
* 🌙 Dark mode

---

## 🧠 Tip

You can place **any folder with images or videos** in the project root — the app will automatically detect and show it.

---

### ✅ You're ready to use it 🚀
