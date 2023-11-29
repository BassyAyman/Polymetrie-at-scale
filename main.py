from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from urllib.parse import urlparse
import redis
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)
redis_client = redis.Redis(host='redis', port=6379, db=0)


def increment_counter(url):
    logger.info(f"Incrementing counter for {url}")
    redis_client.incr(url)


def find_client(domain):
    """
      - POSTGRES_PASSWORD=dev_password
      - POSTGRES_USER=si5_sacc
      - POSTGRES_DB=td_1
    :param domain:
    :return:
    """
    if not domain:
        return None

    try:
        # connect to       - DATABASE_URL=postgresql://si5_sacc:dev_password@database/td_1
        connection = psycopg2.connect(user="si5_sacc",
                                      password="dev_password",
                                      host="database",
                                      port="5432",
                                      database="td_1")
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
    app.run(debug=True, host='0.0.0.0')
