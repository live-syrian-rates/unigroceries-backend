## 1️⃣ Replace `app.py` with a clean final version

Open `C:\data\products\unigroceries-backend\app.py` in VS Code / Notepad.

Delete **everything** in that file and paste this exact code:

```python
from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# ------------------------------------------------------------
# 1. PATH CONFIGURATION
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_DIR = os.path.join(DATA_DIR, "products")


def read_csv(relative_path: str):
    """
    Read a CSV file located under data/ and return list[dict].
    Example relative_path: "products/Snacks.csv" or "message.csv"
    """
    full_path = os.path.join(DATA_DIR, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"CSV not found: {full_path}")

    with open(full_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------
# 2. PRODUCTS ENDPOINT
# ------------------------------------------------------------
@app.route("/products", methods=["GET"])
def products():
    """
    GET /products
    GET /products?category=Snacks
    GET /products?category=Bakery
    etc.

    If category is given, load data/products/<Category>.csv
    Otherwise, fall back to legacy products.csv at root.
    """
    category = request.args.get("category")

    if category:
        filename = f"{category}.csv"
        relative_path = f"products/{filename}"
        full_path = os.path.join(PRODUCTS_DIR, filename)

        if not os.path.exists(full_path):
            return jsonify({"error": f"Category '{category}' not found"}), 404

        return jsonify(read_csv(relative_path))

    # Legacy single file behaviour
    return jsonify(read_csv("products.csv"))


# ------------------------------------------------------------
# 3. MESSAGE ENDPOINT (state + message + news)
# ------------------------------------------------------------
@app.route("/message", methods=["GET"])
def message():
    """
    Reads data/message.csv, expected headers:
      state,message,news

    Returns JSON:
      { state: 0 or 1, message: "...", news: "..." }
    """
    rows = read_csv("message.csv")
    row = rows[0] if rows else {}

    # Accept state under "state" or "State" and tolerate weird values
    raw = row.get("state") or row.get("State") or "0"
    raw_str = str(raw).strip()

    if raw_str in ("1", "on", "ON", "On", "true", "True"):
        state_num = 1
    elif raw_str in ("0", "off", "OFF", "Off", "false", "False", ""):
        state_num = 0
    else:
        # Fallback: if it contains "1" but not "0" => 1, otherwise 0
        if "1" in raw_str and "0" not in raw_str:
            state_num = 1
        else:
            state_num = 0

    return jsonify({
        "state": state_num,
        "message": row.get("message", ""),
        "news": row.get("news", ""),
    })


# ------------------------------------------------------------
# 4. HEALTH CHECK
# ------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return "UniGroceries backend is running."


@app.route("/health", methods=["GET"])
def health():
    """
    Small helper so we can quickly see if server is alive & paths exist.
    """
    return jsonify({
