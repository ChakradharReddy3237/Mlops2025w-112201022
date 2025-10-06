#!/bin/bash
set -euo pipefail

SKIP_DB=0
if ! command -v sqlite3 >/dev/null; then
	echo "sqlite3 not found: will skip DB initialization from question1.sql"
	SKIP_DB=1
fi
command -v uv >/dev/null || { echo "uv is required"; exit 1; }
if ! command -v wget >/dev/null && ! command -v curl >/dev/null; then
	echo "wget or curl is required"; exit 1
fi

DATA_DIR="data"
mkdir -p "$DATA_DIR"

URL="https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
EXCEL_FILE="$DATA_DIR/online_Retail.xlsx"

echo "Downloading Online Retail dataset..."
if command -v wget >/dev/null; then
	wget -O "$EXCEL_FILE" "$URL"
else
	curl -L -o "$EXCEL_FILE" "$URL"
fi

echo "Converting Excel to CSV..."
uv run convert_data.py

echo "Removing the Excel File"
rm -rf "$EXCEL_FILE"

if [ "$SKIP_DB" -eq 0 ]; then
	DB_FILE="question1.db"
	sqlite3 "$DB_FILE" < question1.sql
	echo "Database $DB_FILE initialized from SQL file!"
else
	echo "Skipping DB initialization. Running question1.py will initialize schema automatically."
fi
