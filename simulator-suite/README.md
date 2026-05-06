# Simulator Suite

> **An interactive virtual memory simulator** that visualizes and compares FIFO, LRU, and Optimal page replacement algorithms with step-by-step animation, performance analytics, and export capabilities.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![Tests](https://img.shields.io/badge/Tests-31%20passed-brightgreen) ![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🚀 Quick Start

```bash
# 1. Navigate to the project
cd simulator-suite

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python app.py

# 4. Open in browser
# http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
simulator-suite/
├── app.py                    # Flask application factory + entry point
├── config.py                 # Environment-based configuration
├── requirements.txt
├── .env                      # Environment variables (edit for production)
├── .gitignore
│
├── algorithms/
│   ├── __init__.py           # Registry of all algorithms
│   ├── fifo.py               # First In First Out
│   ├── lru.py                # Least Recently Used (OrderedDict)
│   └── optimal.py            # Bélády's Optimal Algorithm
│
├── services/
│   └── simulator_service.py  # Input validation + algorithm orchestration
│
├── routes/
│   └── api_routes.py         # REST API Blueprint
│
├── tests/
│   ├── test_fifo.py          # 10 unit tests
│   ├── test_lru.py           # 10 unit tests
│   └── test_optimal.py       # 11 unit tests
│
├── templates/
│   └── index.html            # SPA entry point (5-tab interface)
│
└── static/
    ├── css/style.css         # Full design system (dark theme, glassmorphism)
    └── js/script.js          # SPA logic, animations, charts, export
```

---

## 🔌 REST API

### `GET /health`
```json
{
  "status": "success",
  "data": { "healthy": true, "uptime_seconds": 42.5, "version": "1.0.0" }
}
```

### `GET /api/algorithms`
```json
{
  "status": "success",
  "data": {
    "algorithms": [
      { "key": "fifo", "name": "FIFO", "full_name": "First In First Out", "description": "..." },
      { "key": "lru",  "name": "LRU",  "full_name": "Least Recently Used", "description": "..." },
      { "key": "optimal", "name": "Optimal", "full_name": "Optimal (Bélády's Algorithm)", "description": "..." }
    ]
  }
}
```

### `POST /api/simulate`

**Request:**
```json
{
  "reference_string": [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5],
  "frames": 3,
  "algorithms": ["fifo", "lru", "optimal"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": {
      "fifo": {
        "algorithm": "fifo",
        "page_faults": 9,
        "page_hits": 3,
        "hit_ratio": 0.25,
        "fault_rate": 0.75,
        "execution_time_ms": 0.12,
        "steps": [...]
      }
    },
    "comparison": [...],
    "best_algorithm": "optimal",
    "best_algorithm_name": "Optimal"
  }
}
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
# 31 passed in 0.07s
```

---

## 📊 Algorithm Summary

| Algorithm | Time Complexity | Space | Bélády's Anomaly | Requires Future Knowledge |
|-----------|----------------|-------|-------------------|--------------------------|
| FIFO      | O(n·f)         | O(f)  | ✅ Yes            | ❌ No                     |
| LRU       | O(n)           | O(f)  | ❌ No             | ❌ No                     |
| Optimal   | O(n²)          | O(f)  | ❌ No             | ✅ Yes (theoretical only) |

*n = reference string length, f = number of frames*

---

## 🎨 Features

- **5-Tab SPA** — Home, Simulate, Results, Charts, About
- **Step-by-step animation** — Slider and Prev/Next navigation
- **Color-coded states** — 🔴 Page Fault, 🟢 Page Hit
- **Performance metrics** — Faults, Hits, Hit Ratio, Fault Rate, Exec Time
- **4 Chart types** — Bar (faults/hits), Bar (ratios), Line (trend), Doughnut
- **Export** — CSV download + PDF via browser print
- **LocalStorage** — Restores last simulation on page reload
- **Input validation** — Client + server side with clear error messages
- **Responsive** — Mobile-friendly layout

---

## 🚀 Deployment

### Render (recommended)

1. Push project to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `gunicorn app:create_app() --bind 0.0.0.0:$PORT`
5. Add environment variables from `.env`

### Vercel (via serverless adapter)

1. Install vercel: `npm i -g vercel`
2. Create `vercel.json`:
```json
{
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "app.py" }]
}
```
3. Run `vercel deploy`

---

## 🔐 Security Notes

- Input sanitized on both client and server
- Max reference string: 100 values
- Max frames: 20
- JSON Content-Type enforced
- CORS configurable via `CORS_ORIGINS` env var

---

## 📚 Real-World Use Cases

- **Linux kernel**: Uses Clock (approx. LRU) for page frame reclamation
- **Windows NT**: Working Set model with LRU trimming per process
- **Android**: LRU process list for Low Memory Killer
- **Database engines**: Buffer pool managers (PostgreSQL, InnoDB) use LRU variants
- **CPU caches**: Hardware TLB uses approximations of optimal replacement
- **CDN caching**: Edge nodes evict content using LRU/LFU policies

---

## 📝 Sample Inputs

| Name | Reference String | Frames | FIFO Faults | LRU Faults | Optimal Faults |
|------|-----------------|--------|-------------|------------|----------------|
| Classic Textbook | 1,2,3,4,1,2,5,1,2,3,4,5 | 3 | 9 | 10 | 7 |
| Thrashing | 1,2,3,4,5,1,2,3,4,5 | 3 | 10 | 10 | 7 |
| Locality | 1,2,1,3,2,1,4,1,2,3 | 3 | 6 | 4 | 4 |
| Bélády Example | 1,2,3,4,1,2,3,4,1,2,3,4 | 4 | 8 | 8 | 4 |

---

## ⚙️ Configuration (`.env`)

```env
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=change-me-in-production
PORT=5000
MAX_INPUT_LENGTH=100
MAX_FRAMES=20
CORS_ORIGINS=*
```

---

*Built with Flask, Vanilla JS, Chart.js, and a lot of ☕*
