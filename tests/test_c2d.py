import json

import pytest

from avnet.iotconnect.sdk.sdklib.error import C2DDecodeError
from avnet.iotconnect.sdk.sdklib.mqtt import decode_c2d_message, encode_c2d_ack, C2dAck


@pytest.fixture
def command_payload():
    return '{"v":"2.1","ct":0,"cmd":"test enabled","ack":"ABCDEFG"}'


@pytest.fixture
def ota_payload():
    return '{"v":"2.1","ct":1,"cmd":"ota","ack":"ABCDEFG","sw":"1.5","hw":"1","urls":[{"url":"https://URL1","fileName":"file1.bin"}, {"url":"https://URL2","fileName":"file2.bin"}]}'


def test_command_basic(command_payload):
    result = decode_c2d_message(command_payload)
    cmd = result.command

    assert cmd.command_name == "test"
    assert cmd.command_args == ["enabled"]
    assert cmd.ack_id == "ABCDEFG"


def test_command_no_args(command_payload):
    payload = json.loads(command_payload)
    payload["cmd"] = 'no-arguments'
    result = decode_c2d_message(json.dumps(payload))
    assert len(result.command.command_args) == 0


def test_command_missing_fields(command_payload):
    # Start with fresh payload for each test
    payload = json.loads(command_payload)
    del payload['cmd']
    with pytest.raises(C2DDecodeError):
        decode_c2d_message(json.dumps(payload))

    payload = json.loads(command_payload)
    payload['cmd'] = None
    with pytest.raises(C2DDecodeError):
        decode_c2d_message(json.dumps(payload))

    payload = json.loads(command_payload)
    payload['cmd'] = ""
    with pytest.raises(C2DDecodeError):
        decode_c2d_message(json.dumps(payload))


def test_ota_basic(ota_payload):
    result = decode_c2d_message(ota_payload)
    ota = result.ota

    assert ota.urls[0].url == "https://URL1"
    assert ota.urls[1].file_name == "file2.bin"
    assert ota.version == "1.5"


def test_ota_failures(ota_payload):
    # Each test starts with fresh payload
    payload = json.loads(ota_payload)
    del payload["urls"]
    with pytest.raises(C2DDecodeError):
        decode_c2d_message(json.dumps(payload))

    payload = json.loads(ota_payload)
    payload["urls"] = []
    with pytest.raises(C2DDecodeError):
        decode_c2d_message(json.dumps(payload))

    payload = json.loads(ota_payload)
    payload["urls"] = None
    with pytest.raises(C2DDecodeError):
        decode_c2d_message(json.dumps(payload))


def test_ack_encoding(ota_payload):
    ota = decode_c2d_message(ota_payload).ota

    packet = encode_c2d_ack(
        message_type=ota.type,
        ack_id=ota.ack_id,
        status=C2dAck.OTA_DOWNLOAD_DONE,
        message_str="Test"
    )
    assert json.loads(packet) == json.loads('{"d":{"ack":"ABCDEFG","type":1,"st":3,"msg":"Test"}}')
