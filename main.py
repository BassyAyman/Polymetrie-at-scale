from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from urllib.parse import urlparse
import redis
import psycopg2
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
#metrics = PrometheusMetrics(app)
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"),
                           password=os.environ.get("REDIS_PASSWORD"), db=0)


# this commit is the proof the ci/cd pipeline works

def increment_counter(url):
    logger.info(f"Incrementing counter for {url}")
    redis_client.incr(url)


def find_client(domain):
    if not domain:
        return None

    try:
        connection = psycopg2.connect(user=os.environ.get("POSTGRES_USER"),
                                      password=os.environ.get("POSTGRES_PASSWORD"),
                                      host=os.environ.get("POSTGRES_HOST"), port=os.environ.get("POSTGRES_PORT"),
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

def get_all_clients():
    try:
        connection = psycopg2.connect(user=os.environ.get("POSTGRES_USER"),
                                      password=os.environ.get("POSTGRES_PASSWORD"),
                                      host=os.environ.get("POSTGRES_HOST"), port=os.environ.get("POSTGRES_PORT"),
                                      database=os.environ.get("POSTGRES_DB"))
        logger.info("Connected to PostgreSQL")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer")

        # Fetch all the rows
        clients = cursor.fetchall()
        logger.info(f"Clients found: {clients}")

        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None
    return clients


@app.route('/test_db_co', methods=['GET'])
def test_connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        bd = os.environ.get("POSTGRES_DB")
        logger.info(f"Connecting to the PostgreSQL database... {bd}")
        conn = psycopg2.connect(user=os.environ.get("POSTGRES_USER"), password=os.environ.get("POSTGRES_PASSWORD"),
                                host=os.environ.get("POSTGRES_HOST"), port=os.environ.get("POSTGRES_PORT"),
                                database=os.environ.get("POSTGRES_DB"))

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        logger.info('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        logger.info(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.info("An error occured : ")
        logger.info(error)
        return error
    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed.')
            return str(db_version)


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
            increment_counter(client[0])
            return jsonify(success=True, message="Visit counted"), 200

        logger.info(f"Visit from unknown client: {domain}")
        return jsonify(success=False, message="Client not subscribed"), 403

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify(success=False, message="Server error"), 500


# a default route to say hello
@app.route('/')
def hello():
    return 'It works! (main.py modified 13/12/2023 16:02)'


# Add prometheus wsgi middleware to route /metrics requests
# app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

def get_counter(url):
    # Fetch the counter value for the given URL
    counter = redis_client.get(url)
    
    # If the counter is None (indicating the URL doesn't exist), set it to 0
    if counter is None:
        counter = 0
    else:
        # Convert counter from bytes to int
        counter = int(counter)
    logger.info(f"Counter for {url}, is {counter}")
    return counter

def format_client(client_url):
    # Remove 'http://' or 'https://'
    client_url = re.sub(r'^https?://', '', client_url)
    # Replace non-letter characters with underscores
    metric_name = re.sub(r'[^a-zA-Z]', '_', client_url)
    return metric_name

@app.route('/metrics')
def metrics_endpoint():
    result = 0
    clients = get_all_clients()
    stats = ''
    for client in clients:
        #stats = '#' + stats + ' ' + client[0] + ' ' + str(get_counter(client[0])) + '<br>'
        formated_client = format_client(client[0])
        client_counter = get_counter(client[0])
        stats = stats + formated_client + ' ' + str(client_counter) + '<br>'
        result = result + client_counter
    return stats + '<br>' + 'all_clics_for_polytech ' + str(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
