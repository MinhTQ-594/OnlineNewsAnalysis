# OnlineNewsAnalysis 📰

A full pipeline for **collecting, preprocessing, and analyzing Vietnamese news articles**, with an interactive UI for searching and exploring the data.

---

## 📂 Preprocessed Data

The preprocessed dataset for **EDA and Machine Learning tasks** is available here:

[Google Drive Folder](https://drive.google.com/drive/folders/1DWXkQAwLct8b51FV-qsybNYceGL_aYxG?usp=sharing)

**File to use:** `Indexed_cleanest_data.json`

---

## ⚡ Running the UI

### 1. Index the corpus
```bashV
cd src
python index_corpus.py
````

### 2. Start the FastAPI backend

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the React frontend

```bash
cd frontend
npm install
npm start
```

---

## 📝 Notes

* Make sure you have Python >= 3.9 and Node.js installed.
* The backend exposes endpoints for searching and indexing articles.
* The frontend provides an interactive interface for querying the news corpus.

```

Nếu muốn, mình có thể viết thêm **phiên bản README “cực xịn”** với **hình minh họa, badges, và hướng dẫn chạy nhanh chỉ trong 1 lệnh** để nhìn chuyên nghiệp hơn nữa. Bạn có muốn mình làm không?
```
