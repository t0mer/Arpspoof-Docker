import os
import subprocess

from flask import Flask, request
from flask_restful import Api
from loguru import logger

ROUTER_IP = os.getenv("ROUTER_IP")
INTERFACE_NAME = os.getenv("INTERFACE_NAME")

app = Flask(__name__)
api = Api(app)


@app.route("/")
def default():
    logger.info("Number five is alive!")
    return "Number five is alive!"


@app.route("/status")
def get_status():
    try:
        ip = str(request.args.get("ip"))
        logger.info("Getting state for ip: " + ip)
        cmd = (
            "ps -ef | grep 'arpspoof -i "
            + INTERFACE_NAME
            + " -t "
            + ip
            + " "
            + ROUTER_IP
            + "' | grep -v grep | awk '{print $2}'"
        )
        x = subprocess.check_output([cmd], shell=True)
        if not x:
            return "0"
        else:
            return "1"
    except Exception as e:
        logger.error(str(e))
        return "1"



@app.route("/reconnect")
def reconnect():
    try:
        ip = str(request.args.get("ip"))
        logger.info("reconnecting ip: " + ip)
        cmd = (
            "pkill -f 'arpspoof -i "
            + INTERFACE_NAME
            + " -t "
            + ip
            + " "
            + ROUTER_IP
            + "'"
        )
        subprocess.Popen([cmd], shell=True)
        return "1"
    except Exception as e:
        logger.error(str(e))
        return "0"



@app.route("/disconnect")
def disconnect():
    try:
        ip = str(request.args.get("ip"))
        logger.info("Disconnecting ip: " + ip)
        cmd = "arpspoof -i " + INTERFACE_NAME + " -t " + ip + " " + ROUTER_IP
        subprocess.Popen([cmd], shell=True)
        return "1"
    except Exception as e:
        logger.error(str(e))
        return "0"


if __name__ == "__main__":
    logger.info(f"Arpspoof Manager is up and running")
    app.run(debug=True, host="0.0.0.0", port=7022)
