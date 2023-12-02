#!/usr/bin/python3

import argparse
import socket
import re
import json
import paho.mqtt.publish as mqtt_publish

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
    args = arg_parser.parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.apcupsd_host, args.apcupsd_port))
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
        mqtt_auth = None
        if args.mqtt_user:
            mqtt_auth = {}
            mqtt_auth["username"] = args.mqtt_user
            mqtt_auth["password"] = args.mqtt_password
        mqtt_tls = None
        if args.mqtt_tls_cacert:
            mqtt_tls = {}
            mqtt_tls["ca_certs"] = args.mqtt_tls_cacert
            if args.mqtt_tls_cert:
                mqtt_tls["certfile"] = args.mqtt_tls_cert
                mqtt_tls["keyfile"] = args.mqtt_tls_key
        mqtt_publish.single(
            topic=args.mqtt_topic,
            payload=json.dumps(data, indent=2),
            retain=True,
            hostname=args.mqtt_host,
            port=args.mqtt_port,
            client_id=args.mqtt_client_id,
            auth=mqtt_auth,
            tls=mqtt_tls,
            transport=args.mqtt_transport)

if __name__ == "__main__":
    main()
