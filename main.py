from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from urllib.parse import urlparse
import redis
import psycopg2
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0)


def increment_counter(url):
    logger.info(f"Incrementing counter for {url}")
    redis_client.incr(url)


def find_client(domain):
    if not domain:
        return None

    try:
        connection = psycopg2.connect(user=os.environ.get("POSTGRES_USER"),
                                      password=os.environ.get("POSTGRES_PASSWORD"),
                                      host=os.environ.get("POSTGRES_HOST"),
                                      port=os.environ.get("POSTGRES_PORT"),
                                      database=os.environ.get("POSTGRES_DB"))
        logger.info("Connected to PostgreSQL")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer WHERE websiteURL LIKE %s", ('%' + domain + '%',))

        client = cursor.fetchone()
        logger.info(f"Client found: {client}")

        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None

    return client


@app.route('/track', methods=['POST'])
def track_visit():
    try:
        data = request.get_json()
        logger.info("DATA received: %s", data)

        if not data or 'tracker' not in data:
            return jsonify(success=False, message="Invalid JSON format"), 400

        url = data['tracker']['WINDOW_LOCATION_ORIGIN']
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        logger.info(f"Domain: {domain}")
        client = find_client(domain)

        if client:
            logger.info(f"Visit from {client[0]}")
            increment_counter(url)
            return jsonify(success=True, message="Visit counted"), 200

        logger.info(f"Visit from unknown client: {domain}")
        return jsonify(success=False, message="Client not subscribed"), 403

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify(success=False, message="Server error"), 500


@app.route('/metrics_route')
def metrics_endpoint():
    return metrics


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
