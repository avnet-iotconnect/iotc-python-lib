import datetime
import json
import pytest
from dataclasses import dataclass, asdict

import avnet.iotconnect.sdk.sdklib.mqtt as lib_mqtt


# a fictional nested dataclass that we can use to test encoding with
@pytest.fixture
def sensor_data():
    @dataclass
    class AccelerometerData:
        x: float
        y: float
        z: float

    @dataclass
    class SensorData:
        temperature: float
        humidity: float
        accel: AccelerometerData

    return SensorData(
        humidity=30.43,
        temperature=22.8,
        accel=AccelerometerData(x=0.565, y=0.334, z=0)
    )


def test_dict_encoding():
    packet = lib_mqtt.encode_single_telemetry_record({
        'number': 123,
        'string': "mystring",
        'boolean': True,
        'nested': {'a': 'Value A', 'b': 'Value B'}
    })
    expected = {"d": [{"d": {
        "number": 123,
        "string": "mystring",
        "boolean": True,
        "nested": {"a": "Value A", "b": "Value B"}
    }}]}
    assert json.loads(packet) == expected


def test_timestamp_encoding():
    packet = lib_mqtt.encode_single_telemetry_record(
        values={'number': 123},
        timestamp=datetime.datetime.fromtimestamp(1744830740.478986, datetime.timezone.utc)
    )
    data = json.loads(packet)
    assert data["d"][0]["dt"] == "2025-04-16T19:12:20.000Z"


def test_dataclass_encoding(sensor_data):
    packet = lib_mqtt.encode_single_telemetry_record(asdict(sensor_data))
    data = json.loads(packet)
    assert data["d"][0]["d"]["temperature"] == 22.8
    assert data["d"][0]["d"]["accel"]["x"] == 0.565


def test_multiple_records(sensor_data):
    records = []
    timestamp = datetime.datetime.fromtimestamp(1744830740.478986, datetime.timezone.utc)

    sensor_data.temperature = 44.44
    records.append(lib_mqtt.TelemetryRecord(asdict(sensor_data), timestamp))

    sensor_data.temperature = 33.33
    records.append(lib_mqtt.TelemetryRecord(asdict(sensor_data), timestamp))

    packet = lib_mqtt.encode_telemetry_records(records)
    data = json.loads(packet)
    assert len(data["d"]) == 2
    assert data["d"][0]["d"]["temperature"] == 44.44
