import datetime
import json
import sys
from dataclasses import dataclass, asdict

from avnet.iotconnect.sdk.sdklib.mqtt import format_telemetry_records, format_single_telemetry_record, TelemetryRecord


def check(test_name: str, result_value: str, expected_value: str) -> None:
    # we want to sort keys to easily compare in case json gets built with keys in different order
    a = json.dumps(json.loads(result_value), sort_keys=True)
    b = json.dumps(json.loads(expected_value), sort_keys=True)
    if a == b:
        print(test_name, "SUCCESS. Packet:", result_value)
    else:
        print(test_name, "FAILED", file=sys.stderr)
        print("packet:  ", result_value, file=sys.stderr)
        print("expected:", expected_value, file=sys.stderr)
        sys.exit(-1)

#########

packet = format_single_telemetry_record({
    'number': 123,
    'string': "mystring",
    'boolean': True,
    'nested': {
        'a': 'Value A',
        'b': 'Value B'
    }
})
check(
    "Dict Typing Test",
    packet,
    '{"d":[{"d":{"number":123,"string":"mystring","boolean":true,"nested":{"a":"Value A","b":"Value B"}}}]}'
)

#########

packet = format_single_telemetry_record(
    values={
        'number': 123
    },
    timestamp=datetime.datetime.fromtimestamp(1744830740.478986, datetime.timezone.utc)
)
check(
    "Single Record Timestamp Test",
    packet,
    '{"d":[{"d":{"number":123},"dt":"2025-04-16T19:12:20.000Z"}]}'
)

#########

@dataclass
class ExampleAccelerometerData:
    x: float
    y: float
    z: float

@dataclass
class ExampleSensorData:
    temperature: float
    humidity: float
    accel: ExampleAccelerometerData

data = ExampleSensorData(
        humidity=30.43,
        temperature=22.8,
        accel=ExampleAccelerometerData(
            x=0.565,
            y=0.334,
            z=0,
        )
    )

packet = format_single_telemetry_record(asdict(data))

check(
    "Dataclass Test",
    packet,
    '{"d":[{"d":{"temperature":22.8,"humidity":30.43,"accel":{"x":0.565,"y":0.334,"z":0}}}]}'
)

#########

records: list[TelemetryRecord] = []

data.temperature = 44.44
records.append(TelemetryRecord(asdict(data), timestamp=datetime.datetime.fromtimestamp(1744830740.478986, datetime.timezone.utc)))
data.temperature = 33.33
records.append(TelemetryRecord(asdict(data), timestamp=datetime.datetime.fromtimestamp(1744830740.478986, datetime.timezone.utc)))


packet = format_telemetry_records(records)

check(
    "Multiple Records Tests",
    packet,
    '{"d":[{"d":{"temperature":44.44,"humidity":30.43,"accel":{"x":0.565,"y":0.334,"z":0}},"dt":"2025-04-16T19:12:20.000Z"},{"d":{"temperature":33.33,"humidity":30.43,"accel":{"x":0.565,"y":0.334,"z":0}},"dt":"2025-04-16T19:12:20.000Z"}]}'
)

#########