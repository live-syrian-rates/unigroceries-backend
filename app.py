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
    category = request.args.get("category")

    if category:
        filename = f"{category}.csv"
        relative_path = f"products/{filename}"
        full_path = os.path.join(PRODUCTS_DIR, filename)

        if not os.path.exists(full_path):
            return jsonify({"error": f"Category '{category}' not found"}), 404

        return jsonify(read_csv(relative_path))

    return jsonify(read_csv("products.csv"))


# ------------------------------------------------------------
# 3. MESSAGE ENDPOINT (state + message + news)
# ------------------------------------------------------------
@app.route("/message", methods=["GET"])
def message():
    rows = read_csv("message.csv")
    row = rows[0] if rows else {}

    # Read and normalize state
    raw = row.get("state") or row.get("State") or "0"
    raw_str = str(raw).strip().lower()
    state_num = 1 if raw_str in ("1", "on", "true") else 0

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
    return jsonify({
        "ok": True,
        "data_dir": DATA_DIR,
        "has_products_dir": os.path.isdir(PRODUCTS_DIR),
        "has_message_csv": os.path.exists(os.path.join(DATA_DIR, "message.csv")),
    })


# ------------------------------------------------------------
# 5. RUN SERVER (local dev only)
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
