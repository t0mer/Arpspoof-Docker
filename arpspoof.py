from flask import Flask, request, make_response, render_template, url_for, g, send_from_directory, jsonify
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)




if __name__ == '__main__':
    logger.info(f"Arpspoof Manager is up and running")
    app.run(debug=True, host='0.0.0.0', port=7022)