import psycopg2
import os
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_USER = os.environ.get("CATALOG_API_USER", "catalog_reader")
API_PASS = os.environ.get("CATALOG_API_PASS", "changeme")

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="german_car_market",
        user="postgres",
        password=os.environ["DB_PASSWORD"]
    )

def check_auth(username, password):
    return username == API_USER and password == API_PASS

@app.route("/api/v1/brands", methods=["GET"])
def get_brands():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Vehicle Catalog API"'})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT brand_id, brand_name, country_of_origin, brand_tier FROM brands")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    brands = [
        {"brand_id": r[0], "brand_name": r[1], "country_of_origin": r[2], "brand_tier": r[3]}
        for r in rows
    ]
    return jsonify({"data": brands})


@app.route("/api/v1/models", methods=["GET"])
def get_models():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Vehicle Catalog API"'})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT model_id, brand_id, model_name, body_type, segment FROM models")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    models = [
        {"model_id": r[0], "brand_id": r[1], "model_name": r[2], "body_type": r[3], "segment": r[4]}
        for r in rows
    ]
    return jsonify({"data": models})


@app.route("/api/v1/vehicles", methods=["GET"])
def get_vehicles():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Vehicle Catalog API"'})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT vehicle_id, model_id, model_year, fuel_type, engine_size_liters, 
                          transmission_type, emissions_class FROM vehicles""")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    vehicles = [
        {"vehicle_id": r[0], "model_id": r[1], "model_year": r[2], "fuel_type": r[3],
         "engine_size_liters": float(r[4]) if r[4] else None, "transmission_type": r[5],
         "emissions_class": r[6]}
        for r in rows
    ]
    return jsonify({"data": vehicles})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)