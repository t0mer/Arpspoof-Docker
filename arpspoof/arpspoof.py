from flask import Flask, request, make_response, render_template, url_for, g, send_from_directory, jsonify
from flask_restful import Resource, Api
import os, json, subprocess, time, argparse, datetime, re
from os import environ, path
from json import dumps
from subprocess import call
from loguru import logger


router_ip = os.getenv("ROUTER_IP")
interface_name = os.getenv("INTERFACE_NAME")

app = Flask(__name__)
api = Api(app)



@app.route('/')
def default():
    logger.info("Number five is alive!")
    return "Number five is alive!"


@app.route('/status',methods = ['POST', 'GET'])
def get_status():
    try:
        if request.method == 'POST':
            ip = str(request.form['ip'])
        else:
            ip = str(request.args.get('ip'))
        logger.info("Getting state for ip: " + ip)
        cmd = "ps -ef | grep 'arpspoof -i " + interface_name + " -t "+ ip + " " +router_ip +"' | grep -v grep | awk '{print $2}'"
        x= subprocess.check_output([cmd],shell=True)
        if not x:
            return "0"
        else:
            return "1"
    except Exception as e:
        logger.error(str(e))
        return "1"
 
@app.route('/reconnect',methods = ['POST', 'GET'])
def reconnect():
    try:
        if request.method == 'POST':
            ip = str(request.form['ip'])
        else:
            ip = str(request.args.get('ip'))
        logger.info("reconnecting ip: " + ip)
        cmd = "pkill -f 'arpspoof -i "+ interface_name + " -t " + ip + " "+ router_ip + "'"
        subprocess.Popen([cmd],shell=True)
        return "1"
    except Exception as e:
        logger.error(str(e))
        return "0"

@app.route('/disconnect',methods = ['POST', 'GET'])
def disconnect():
    try:
        if request.method == 'POST':
            ip = str(request.form['ip'])
        else:
            ip = str(request.args.get('ip'))
        logger.info("Disconnecting ip: " + ip)
        cmd = "arpspoof -i " + interface_name +" -t " + ip + " " + router_ip
        subprocess.Popen([cmd],shell=True)
        return "1"
    except Exception as e:
        logger.error(str(e))
        return "0"
if __name__ == '__main__':
    logger.info(f"Arpspoof Manager is up and running")
    app.run(debug=True, host='0.0.0.0', port=7022)
