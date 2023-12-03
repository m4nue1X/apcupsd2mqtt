# apcupsd2mqtt

`apcupsd2mqtt.py` is a simple Ptyhon script which fetches information on the UPS status from `apcupsd` and publishes it to an MQTT broker.

Example usage:
```
apcupsstatus.py --mqtt_topic=apcupsd/ups_status --mqtt_user=<mqtt-user> --mqtt_password=<mqtt-password> --mqtt_host=<mqtt-host>> --mqtt_port=8883 --mqtt_tls_cacert=/etc/ssl/mqtt/cacert.pem --hass_config=True
```

**Requirements:**
* Python3
* paho-mqtt
* apcupsd
* an MQTT broker to publish to (e. g. mosquitto)

