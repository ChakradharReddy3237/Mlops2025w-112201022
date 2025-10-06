# MLOps Assignment 4 (uv version)

A clean uv-based solution using the UCI Online Retail dataset with SQLite and MongoDB models, plus CRUD benchmarking.

## Prerequisites
- Python 3.10+
- uv
- SQLite 3 CLI (`sqlite3`)
- MongoDB (local) or MongoDB Atlas

## Setup
```bash
# from Assignment_4_UV/
uv python install 3.10
uv sync
```

## Data
```bash
bash get_data.sh
```

## Run
```bash
# Q1: SQLite
uv run python question1.py

# Q2: Build MongoDB collections (local)
uv run python question2.py

# Q3: CRUD benchmark
export MPLBACKEND=Agg
uv run python question3.py

# Q4: Upload to Atlas (or local fallback)
# For real Atlas: get connection string from Atlas dashboard
# export MONGODB_URI="mongodb+srv://user:pass@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# For local: export MONGODB_URI="mongodb://localhost:27017/" or just run without setting it
uv run python question4.py
```

## Report -> PDF
```bash
bash export_report.sh
# outputs ../Assignment 4.pdf
```

## Lint/Typecheck (optional)
```bash
uv run ruff check .
uv run mypy .
```

