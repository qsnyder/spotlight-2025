from flask import Flask, request
from netmiko import ConnectHandler
import requests
import json
import re

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        raw_output = request.json["result"]["_raw"]
        host_address = request.json["result"]["host"]
        python_output = json.dumps(raw_output)
        modified_output = '{"text": %s}' % (python_output)
        requests.post(
            "WEBHOOK-URL",
            headers={"Content-Type": "application/json"},
            data=modified_output,
            verify=False,
        )
        if (
            "%LINK-5-CHANGED:" in raw_output
            and "changed state to administratively down" in raw_output
        ):
            interface = re.findall(r"(GigabitEthernet\d+(?:\/)\d+?)", raw_output)
            device = ConnectHandler(
                host=host_address,
                username="cisco",
                password="cisco",
                device_type="cisco_ios",
            )
            INTERFACE = interface[0]
            commands = [f"interface {INTERFACE}", f"no shutdown"]
            device.send_config_set(commands)
            print(f"Interface {INTERFACE} on {host_address} has been re-enabled")
        return "Webhook received!"


app.run(host="0.0.0.0", debug=True, port=8888)
