from flask import Flask, request, make_response, render_template, url_for, g, send_from_directory, jsonify
from flask_restful import Resource, Api
import os, json, subprocess, time, broadlink, argparse, datetime, re
from os import environ, path
from json import dumps
from subprocess import call
from loguru import logger


app = Flask(__name__)
api = Api(app)



@app.route('/')
def default():
    logger.info("Number five is alive!")
    return "Number five is alive!"



if __name__ == '__main__':
    logger.info(f"Arpspoof Manager is up and running")
    app.run(debug=True, host='0.0.0.0', port=7022)