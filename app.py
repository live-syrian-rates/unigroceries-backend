from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# ---------- helpers ----------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def read_csv(filename):
    """Read any CSV inside DATA_DIR and return list[dict]"""
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ---------- routes ----------
@app.route("/products", methods=["GET"])
def products():
    category = request.args.get("category")          # ?category=Snacks
    if category:
        # map pretty category name → file name we created
        filename = f"{category}.csv"
        path = os.path.join(DATA_DIR, "products", filename)
        if not os.path.exists(path):
            return jsonify({"error": "Category not found"}), 404
        return jsonify(read_csv(f"products/{filename}"))
    # no category → return legacy single file (keep old behaviour)
    return jsonify(read_csv("products.csv"))

@app.route("/message", methods=["GET"])
def message():
    rows = read_csv("message.csv")
    return jsonify([r["message"] for r in rows])

# ---------- health ----------
@app.route("/", methods=["GET"])
def home():
    return "UniGroceries backend is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
