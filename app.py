from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from backend import rag, create_database
import os



app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

@app.route('/')
def home():
    """The main page of the application.

    Returns:
        The main HTML page.
    """
    return render_template('index.html')

@app.route('/TestConnection', methods=['POST'])
def test_splunk_connection():
    """Test the connection to the given Splunk instance.

    POST parameters:
    - host: The Splunk host.
    - port: The Splunk port.
    - username: The Splunk username.
    - password: The Splunk password.

    Returns:
    - 200 OK if the connection was successful.
    - 400 Bad Request if any of the parameters are missing.
    - 401 Unauthorized if the username/password combination is incorrect.
    - 500 Internal Server Error if the connection could not be established.

    """
    try:

        # Get the request JSON data
        data = request.get_json()

        # Get the parameters from the request data
        host = data.get('host')
        port = data.get('port')
        user = data.get('user')
        token = data.get('token')

        # Validate the parameters
        print("Received inputs for testing connection:")
        print(host, port, user, token)

        if not all([host, port, user, token]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Test Connection here
        status_code, test_connection = 200, True

        if status_code == 200:
            return jsonify({'connection': True}), 200
        elif status_code == 401:
            return jsonify({'connection': False}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/AnalyzeLogs', methods=['POST'])
def analyze_logs():
    """
    Analyze logs for a given application over a specified time range.

    POST parameters:
    - source_type: The type of log source. Valid values are 'syslog', 'http:access', and 'custom:app'.
    - start_time: The starting time of the time range to analyze in ISO 8601 format.
    - end_time: The ending time of the time range to analyze in ISO 8601 format.
    - application_name: The name of the application to analyze.
    - query: User's query

    Returns:
    - 200 OK if the analysis was successful.
    - 400 Bad Request if any of the parameters are missing or invalid.
    - 500 Internal Server Error if the analysis could not be completed.
    """
    try:
        # Get the request JSON data
        data = request.get_json()

        # Get the parameters from the request data
        source_type = data.get('source_type')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        application_name = data.get('application_name')
        query = data.get('query')

        # Validate the parameters
        if not all([source_type, start_time, end_time, application_name, query]):
            return jsonify({'error': 'Missing required parameters'}), 400


        # Analyze the logs using the provided parameters
        # Replace this with your actual log analysis logic

        print("Received inputs for Analyzing logs:")
        print(f"Source Type: {source_type}")
        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")
        print(f"Application Name: {application_name}")
        print(f"Query: {query}")

        if not os.path.exists(f"./chroma/{application_name}"):
            create_database.create(application_name)

        output = rag.analyse(application_name, start_time, end_time, query)

        # Return the analyzed log data
        return jsonify(output), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
