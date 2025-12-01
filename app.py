from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# ------------------------------------------------------------
# 📁 1. PATH CONFIGURATION
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_DIR = os.path.join(DATA_DIR, "products")

def read_csv(relative_path):
    """Read CSV located under data/ and return list[dict]"""
    full_path = os.path.join(DATA_DIR, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"CSV not found: {full_path}")

    with open(full_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------
# 🛒 2. PRODUCTS ENDPOINT
# ------------------------------------------------------------
@app.route("/products", methods=["GET"])
def products():
    # Example: /products?category=Snacks
    category = request.args.get("category")

    if category:
        filename = f"{category}.csv"
        relative_path = f"products/{filename}"
        full_path = os.path.join(PRODUCTS_DIR, filename)

        if not os.path.exists(full_path):
            return jsonify({"error": f"Category '{category}' not found"}), 404

        return jsonify(read_csv(relative_path))

    # Legacy fallback (old behavior)
    return jsonify(read_csv("products.csv"))


# ------------------------------------------------------------
# 📰 3. MESSAGE ENDPOINT (state, message, news)
# ------------------------------------------------------------
@app.route("/message", methods=["GET"])
def message():
    rows = read_csv("message.csv")

    # Expect exactly 1 row
    row = rows[0] if rows else {}

    return jsonify({
        "state": int(row.get("state", 0)),
        "message": row.get("message", ""),
        "news": row.get("news", "")
    })


# ------------------------------------------------------------
# ❤️ 4. HEALTH CHECK
# ------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return "UniGroceries backend is running."


# ------------------------------------------------------------
# 🚀 5. RUN SERVER
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
