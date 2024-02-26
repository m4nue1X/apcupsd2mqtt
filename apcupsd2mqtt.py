#!/usr/bin/python3

import argparse
import socket
import re
import json
from datetime import datetime
import paho.mqtt.publish as mqtt_publish

def get_sensor_config(field_name, field_value, discovery_prefix, node_id, node_name, topic):
    name = field_name.lower()
    config_topic = discovery_prefix + "/sensor/" + node_id + "-" + name + "/config"
    value_template = "{{ value_json." + field_name + ".value }}" if isinstance(field_value, dict) else "{{ value_json." + field_name + " }}"
    config = {}
    if name == "status":
        config["device_class"] = "enum"
        config["name"] = node_name + " status"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "linev":
        config["device_class"] = "voltage"
        config["name"] = node_name + " line voltage"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "V"
        config["value_template"] = value_template
    elif name ==  "loadpct":
        config["name"] = node_name + " load percentage"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "%"
        config["value_template"] = value_template
    elif name ==  "bcharge":
        config["device_class"] = "battery"
        config["name"] = node_name + " battery charge"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "%"
        config["value_template"] = value_template
    elif name ==  "timeleft":
        config["name"] = node_name + " time left"
        config["device_class"] = "duration"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "min"
        config["value_template"] = value_template
    elif name ==  "mbattchg":
        config["name"] = node_name + " shutdown at battery percentage"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "%"
        config["value_template"] = value_template
    elif name ==  "mintimel":
        config["name"] = node_name + " shutdown at remaining time"
        config["device_class"] = "duration"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "min"
        config["value_template"] = value_template
    elif name ==  "sense":
        config["device_class"] = "enum"
        config["name"] = node_name + " sensitivity"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "lotrans":
        config["device_class"] = "voltage"
        config["name"] = node_name + " low voltage threshold"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "V"
        config["value_template"] = value_template
    elif name ==  "hitrans":
        config["device_class"] = "voltage"
        config["name"] = node_name + " high voltage threshold"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "V"
        config["value_template"] = value_template
    elif name ==  "battv":
        config["device_class"] = "voltage"
        config["name"] = node_name + " battery voltage"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "V"
        config["value_template"] = value_template
    elif name ==  "lastxfer":
        config["name"] = node_name + " last transfer reason"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "numxfers":
        config["name"] = node_name + " number of transfers"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "xonbatt":
        config["device_class"] = "timestamp"
        config["name"] = node_name + " last transfer to battery"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "tonbatt":
        config["device_class"] = "duration"
        config["name"] = node_name + " last duration on battery"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "s"
        config["value_template"] = value_template
    elif name ==  "cumonbatt":
        config["device_class"] = "duration"
        config["name"] = node_name + " total duration on battery"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "s"
        config["value_template"] = value_template
    elif name ==  "xoffbatt":
        config["device_class"] = "timestamp"
        config["name"] = node_name + " last transfer to mains"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "selftest":
        config["device_class"] = "enum"
        config["name"] = node_name + " selftest running"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "serialno":
        config["name"] = node_name + " serial number"
        config["state_topic"] = topic
        config["value_template"] = value_template
    elif name ==  "nominv":
        config["device_class"] = "voltage"
        config["name"] = node_name + " nominal voltage"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "V"
        config["value_template"] = value_template
    elif name ==  "nombattv":
        config["device_class"] = "voltage"
        config["name"] = node_name + " nominal battery voltage"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "V"
        config["value_template"] = value_template
    elif name ==  "nompower":
        config["device_class"] = "power"
        config["name"] = node_name + " nominal power"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "W"
        config["value_template"] = value_template
    elif name ==  "currpwr_calc":
        config["device_class"] = "power"
        config["name"] = node_name + " current power consumption load (calculated)"
        config["state_topic"] = topic
        config["unit_of_measurement"] = "W"
        config["value_template"] = value_template
    if len(config) > 0:
        return config_topic, config
    return None, None

def date_time_to_iso(value):
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S %z").isoformat()
    except:
        return None

def fix_date_time(data):
    for key in data:
        if key == "APC" or key == "DATE" or key == "STARTTIME" or key == "XONBATT" or key == "XOFFBATT" or key == "END APC":
            data[key] = date_time_to_iso(data[key])
        if key == "TIMELEFT" or key == "MINTIMEL":
            data[key]["value"] = int(data[key]["value"])

def read_data(hostname, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostname, port))
        status_str = "status".encode('ascii')
        s.send(len(status_str).to_bytes(2, 'big'))
        s.send(status_str)
        data = {}
        while True:
            msg_length = int.from_bytes(s.recv(2), 'big')
            if msg_length == 0:
                break
            msg = s.recv(msg_length)
            name_value_match = re.search(r'([A-Za-z0-9]+)\s*:\s*(.*)\s*', msg.decode('ascii'))
            value_unit_match = re.search(r'(.*)\s+(Volts|Watts|Percent|Minutes|Seconds)', name_value_match.group(2))
            if(value_unit_match):
                data[name_value_match.group(1)] = {'value': float(value_unit_match.group(1)), 'unit': value_unit_match.group(2)}
            else:
                data[name_value_match.group(1)] = name_value_match.group(2)
        return data
    return None

def publish(hostname, port, client_id, username, password, tls_cacert, tls_cert, tls_key, transport, messages):
    mqtt_auth = None
    if username:
        mqtt_auth = {}
        mqtt_auth["username"] = username
        mqtt_auth["password"] = password
    mqtt_tls = None
    if tls_cacert:
        mqtt_tls = {}
        mqtt_tls["ca_certs"] = tls_cacert
        if tls_cert:
            mqtt_tls["certfile"] = tls_cert
            mqtt_tls["keyfile"] = tls_key
    mqtt_publish.multiple(
        messages,
        hostname=hostname,
        port=port,
        client_id=client_id,
        auth=mqtt_auth,
        tls=mqtt_tls,
        transport=transport)

def calc_power(data):
    if data["NOMPOWER"] and data["LOADPCT"]:
        return data["NOMPOWER"]["value"] * data["LOADPCT"]["value"] / 100
    return -1

def main():
    arg_parser = argparse.ArgumentParser(prog="apcupsd2mqtt", description="Polls data from apcupsd and publishes it to an MQTT server as JSON")
    arg_parser.add_argument("--apcupsd_host", action="store", default="localhost")
    arg_parser.add_argument("--apcupsd_port", action="store", default="3551", type=int)
    arg_parser.add_argument("--mqtt_host", action="store", default="localhost")
    arg_parser.add_argument("--mqtt_port", action="store", default="1883", type=int)
    arg_parser.add_argument("--mqtt_client_id", action="store")
    arg_parser.add_argument("--mqtt_user", action="store")
    arg_parser.add_argument("--mqtt_password", action="store")
    arg_parser.add_argument("--mqtt_tls_cacert", action="store")
    arg_parser.add_argument("--mqtt_tls_cert", action="store")
    arg_parser.add_argument("--mqtt_tls_key", action="store")
    arg_parser.add_argument("--mqtt_transport", action="store", default="tcp")
    arg_parser.add_argument("--mqtt_topic", action="store", required=True)
    arg_parser.add_argument("--hass_config", action="store_true", default=False)
    arg_parser.add_argument("--hass_discovery_prefix", action="store", default="homeassistant")
    arg_parser.add_argument("--hass_node_id", action="store", default="UPS")
    arg_parser.add_argument("--hass_node_name", action="store", default="UPS")
    arg_parser.add_argument("--calculate_power", action="store_true", default=True)
    arg_parser.add_argument("--date_time_iso", action="store_true", default=True)
    arg_parser.add_argument("--dry_run", action="store_true", default=False)
    args = arg_parser.parse_args()

    data = read_data(args.apcupsd_host, args.apcupsd_port)
    if args.calculate_power:
        data["currpwr_calc"] = { "value": calc_power(data), "unit": "Watts" }
    if args.date_time_iso:
        fix_date_time(data)
    messages = []
    data_msg = {}
    data_msg["topic"] = args.mqtt_topic
    data_msg["retain"] = True
    data_msg["payload"] = json.dumps(data, indent=2)
    messages.append(data_msg)
    if args.hass_config:
        for key in data:
            topic_name, config = get_sensor_config(key, data[key], args.hass_discovery_prefix, args.hass_node_id, args.hass_node_name, args.mqtt_topic)
            if topic_name:
                config_msg = {}
                config_msg["topic"] = topic_name
                config_msg["retain"] = True
                config_msg["payload"] = json.dumps(config, indent=2)
                messages.append(config_msg)
    if not args.dry_run:
    	publish(args.mqtt_host, args.mqtt_port, args.mqtt_client_id, args.mqtt_user, args.mqtt_password, args.mqtt_tls_cacert, args.mqtt_tls_cert, args.mqtt_tls_key, args.mqtt_transport, messages)
    else:
    	print(f"{messages}")

if __name__ == "__main__":
    main()
