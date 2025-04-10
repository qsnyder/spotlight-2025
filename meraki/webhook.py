from flask import Flask, request
import meraki
import requests
import json
import os
from dotenv import load_dotenv
from ipcalc import Network

load_dotenv()
API_KEY = os.getenv("API_KEY")
SERIAL = os.getenv("SERIAL")
NETBOX_KEY = os.getenv("NETBOX_KEY")
NETBOX_URL = os.getenv("NETBOX_URL")

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        raw_output = request.json["result"]["_raw"]
        python_output = json.dumps(raw_output)
        modified_output = '{"text": %s}' % (python_output)
        response = requests.post(
            "WEBHOOK_URL_HERE",
            headers={"Content-Type": "application/json"},
            data=modified_output,
            verify=False,
        )
        jsonified_raw_output = json.loads(raw_output)
        if "apiChange" not in jsonified_raw_output["event"]["alertData"]["changes"]:
            nb_response = requests.get(
                NETBOX_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Token {NETBOX_KEY}",
                },
            ).json()
            network_with_cidr = nb_response["primary_ip"]["address"]
            network = Network(network_with_cidr)
            static_ip = str(network.to_tuple()[0])
            static_subnet_mask = str(network.netmask())
            static_gateway_ip = nb_response["custom_fields"]["gateway_ip"]
            # Use this if you're wishing to revert from the payload, rather than netbox
            # alert_information = jsonified_raw_output["event"]["alertData"]["changes"]["staticIp84424578629651"]["oldText"]
            # static_ip = alert_information["iP"]
            # static_subnet_mask = alert_information["subnet mask"]
            # static_gateway_ip = alert_information["gateway"]
            # static_dns_1 = alert_information["primary DNS"]
            # static_dns_2 = alert_information["secondary DNS"]
            # vlan = alert_information["vLAN"]
            dashboard = meraki.DashboardAPI(API_KEY)
            change_correction = dashboard.devices.updateDeviceManagementInterface(
                serial=SERIAL,
                wan1={
                    "wanEnabled": "enabled",
                    "usingStaticIp": True,
                    "staticIp": static_ip,
                    "staticGatewayIp": static_gateway_ip,
                    "staticSubnetMask": static_subnet_mask,
                    # 'staticDns': [static_dns_1, static_dns_2],
                    # 'vlan': vlan
                },
            )
        return "Webhook received!"


app.run(host="0.0.0.0", debug=True, port=8888)
