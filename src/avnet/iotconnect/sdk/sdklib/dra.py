# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> and Zackary Andraka <zackary.andraka@avnet.com> et al.

import json
import urllib.parse
import urllib.request
from typing import Final, Union, Optional
from urllib.error import HTTPError, URLError

from avnet.iotconnect.sdk.sdklib.config import DeviceProperties
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError
from avnet.iotconnect.sdk.sdklib.protocol.discovery import IotcDiscoveryResponseJson
from avnet.iotconnect.sdk.sdklib.protocol.identity import ProtocolIdentityPJson, ProtocolMetaJson, \
    ProtocolIdentityResponseJson
from avnet.iotconnect.sdk.sdklib.util import deserialize_dataclass


class KvsConfig:
    """Kinesis Video Streaming configuration"""

    def __init__(self, vs_data):
        if vs_data is not None:
            self.enabled = True
            self.credential_endpoint = vs_data.url
            self.auto_start = vs_data.as_ if vs_data.as_ is not None else False
        else:
            self.enabled = False
            self.credential_endpoint = None
            self.auto_start = False


class DeviceIdentityData:
    def __init__(self, mqtt: ProtocolIdentityPJson, metadata: ProtocolMetaJson):
        self.host = mqtt.h
        self.client_id = mqtt.id
        self.username = mqtt.un
        self.topics = mqtt.topics

        self.pf = metadata.pf
        self.is_edge_device = metadata.edge
        self.is_gateway_device = metadata.gtw
        self.protocol_version = str(metadata.v)

        # NEW: KVS configuration
        self.kvs = KvsConfig(mqtt.vs)


class DraDiscoveryUrl:
    method: str = "GET"  # To clarify that get should be used to parse the response
    API_URL_FORMAT: Final[str] = "https://discovery.iotconnect.io/api/v2.1/dsdk/cpId/%s/env/%s?pf=%s"

    def __init__(self, config: DeviceProperties):
        self.config = config

    def get_api_url(self) -> str:
        return DraDiscoveryUrl.API_URL_FORMAT % (
            urllib.parse.quote(self.config.cpid, safe=''),
            urllib.parse.quote(self.config.env, safe=''),
            urllib.parse.quote(self.config.platform, safe='')
        )


class DraIdentityUrl:
    UID_API_URL_FORMAT: Final[str] = "%s/uid/%s"

    def __init__(self, base_url):
        self.base_url = base_url

    method: str = "GET"  # To clarify that get should be used to parse the response

    def get_uid_api_url(self, config: DeviceProperties) -> str:
        return DraIdentityUrl.UID_API_URL_FORMAT % (
            self.base_url,
            urllib.parse.quote(config.duid, safe='')
        )

    def _validate_identity_response(self, ird: ProtocolIdentityResponseJson):
        # TODO: validate and throw DeviceConfigError
        pass


class DraDeviceInfoParser:
    EC_RESPONSE_MAPPING = [
        "OK – No Error",
        "Device not found. Device is not whitelisted to platform.",
        "Device is not active.",
        "Un-Associated. Device has not any template associated with it.",
        "Device is not acquired. Device is created but it is in release state.",
        "Device is disabled. It's disabled from broker by Platform Admin",
        "Company not found as SID is not valid",
        "Subscription is expired.",
        "Connection Not Allowed.",
        "Invalid Bootstrap Certificate.",
        "Invalid Operational Certificate."
    ]

    @classmethod
    def _parsing_common(cls, what: str, rd: Union[IotcDiscoveryResponseJson, ProtocolIdentityResponseJson]):
        """ Helper to parse either discovery or identity response common error fields """

        ec_message = 'not available'
        has_error = False
        if rd.d is not None:
            if rd.d.ec != 0:
                has_error = True
                if rd.d.ec <= len(cls.EC_RESPONSE_MAPPING):
                    ec_message = 'ec=%d (%s)' % (rd.d.ec, cls.EC_RESPONSE_MAPPING[rd.d.ec])
                else:
                    ec_message = 'ec==%d' % rd.d.ec
        else:
            has_error = True

        if rd.status != 200:
            has_error = True

        if has_error:
            raise DeviceConfigError(
                '%s failed. Error: "%s" status=%d message=%s' % (
                    what,
                    ec_message,
                    rd.status,
                    rd.message or "(message not available)"
                )
            )

    @classmethod
    def parse_discovery_response(cls, discovery_response: str) -> str:
        """ Parses discovery response JSON and Returns base URL or raises DeviceConfigError """

        drd: IotcDiscoveryResponseJson
        try:
            drd = deserialize_dataclass(IotcDiscoveryResponseJson, json.loads(discovery_response))
        except json.JSONDecodeError as json_error:
            raise DeviceConfigError("Discovery JSON Parsing Error: %s" % str(json_error))
        cls._parsing_common("Discovery", drd)

        if drd.d.bu is None:
            raise DeviceConfigError("Discovery response is missing base URL")

        return drd.d.bu

    @classmethod
    def parse_identity_response(cls, identity_response: str) -> DeviceIdentityData:
        ird: ProtocolIdentityResponseJson
        try:
            ird = deserialize_dataclass(ProtocolIdentityResponseJson, json.loads(identity_response))
        except json.JSONDecodeError as json_error:
            raise DeviceConfigError("Identity JSON Parsing Error: %s" % str(json_error))
        cls._parsing_common("Identity", ird)

        return DeviceIdentityData(ird.d.p, ird.d.meta)


class DeviceRestApi:
    def __init__(self, config: DeviceProperties, verbose: Optional[bool] = False):
        self.config = config
        self.verbose = verbose

    def get_identity_data(self) -> DeviceIdentityData:
        try:
            if self.verbose:
                print("Requesting Discovery Data %s..." % DraDiscoveryUrl(self.config).get_api_url())
            resp = urllib.request.urlopen(urllib.request.Request(DraDiscoveryUrl(self.config).get_api_url()))
            discovery_base_url = DraDeviceInfoParser.parse_discovery_response(resp.read())

            if self.verbose:
                print(
                    "Requesting Identity Data %s..." % DraIdentityUrl(discovery_base_url).get_uid_api_url(self.config))
            resp = urllib.request.urlopen(DraIdentityUrl(discovery_base_url).get_uid_api_url(self.config))
            identity_response = DraDeviceInfoParser.parse_identity_response(resp.read())
            return identity_response

        except HTTPError as http_error:
            raise DeviceConfigError(http_error)

        except URLError as url_error:
            raise DeviceConfigError(str(url_error))

    def get_aws_credentials(
            self,
            credential_endpoint: str,
            device_cert_path: str,
            device_pkey_path: str,
            server_ca_cert_path: str,
            thing_name: str
    ) -> Optional[tuple]:
        """
        Fetch AWS credentials from an IoT credential endpoint for Kinesis Video Streaming.

        Args:
            credential_endpoint: HTTPS URL ending with '/credentials' for the AWS role alias
            device_cert_path: Path to the device certificate file
            device_pkey_path: Path to the device private key file
            server_ca_cert_path: Path to the server CA certificate file
            thing_name: The IoT thing name (MQTT client ID)

        Returns:
            Tuple of (accessKeyId, secretAccessKey, sessionToken) on success, None on failure
        """
        import ssl

        if not credential_endpoint:
            print("AWS credential endpoint is required")
            return None

        url = credential_endpoint.strip()
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme != "https" or not url.endswith("/credentials"):
                print(f"Bad role-alias URL: {url}. URL must use HTTPS and end with '/credentials'")
                return None
            if not parsed.netloc:
                print(f"Invalid URL format: {url}. Missing domain name")
                return None
        except Exception as e:
            print(f"Failed to parse URL '{url}': {e}")
            return None

        if self.verbose:
            print(f"AWS credentials endpoint: {url}")
            print(f"Using Thing name: {thing_name}")

        try:
            ssl_context = ssl.create_default_context(cafile=server_ca_cert_path)
            ssl_context.load_cert_chain(certfile=device_cert_path, keyfile=device_pkey_path)

            request = urllib.request.Request(
                url,
                headers={"x-amzn-iot-thingname": thing_name}
            )
            response = urllib.request.urlopen(request, context=ssl_context)
            res_load = json.loads(response.read().decode('utf-8'))

            if self.verbose:
                print(res_load)

            return (
                res_load["credentials"]["accessKeyId"],
                res_load["credentials"]["secretAccessKey"],
                res_load["credentials"]["sessionToken"]
            )

        except HTTPError as e:
            print(f"HTTP error obtaining credentials: {e.code} {e.reason}")
            return None
        except URLError as e:
            print(f"Error obtaining credentials: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing credentials response: {e}")
            return None