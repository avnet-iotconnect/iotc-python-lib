# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> and Zackary Andraka <zackary.andraka@avnet.com> et al.

import json
import urllib.parse
import urllib.request
import datetime
import ssl

from typing import Final, Union, Optional
from urllib.error import HTTPError, URLError

from avnet.iotconnect.sdk.sdklib.config import DeviceProperties, DeviceTlsCredentials
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError, ClientError
from avnet.iotconnect.sdk.sdklib.protocol.credentials import CredentialsResponseJson
from avnet.iotconnect.sdk.sdklib.protocol.discovery import IotcDiscoveryResponseJson
from avnet.iotconnect.sdk.sdklib.protocol.identity import ProtocolIdentityPJson, ProtocolMetaJson, ProtocolIdentityResponseJson, ProtocolVideoStreamingJson, ProtocolFsJson
from avnet.iotconnect.sdk.sdklib.util import deserialize_dataclass


class DeviceIdentityData:
    def __init__(
            self,
            mqtt: ProtocolIdentityPJson,
            metadata: ProtocolMetaJson,
            vs: Optional[ProtocolVideoStreamingJson] = None,
            fs: Optional[ProtocolFsJson] = None

    ):
        self.host = mqtt.h
        self.client_id = mqtt.id
        self.username = mqtt.un
        self.topics = mqtt.topics

        self.pf = metadata.pf
        self.is_edge_device = metadata.edge
        self.is_gateway_device = metadata.gtw
        self.protocol_version = str(metadata.v)

        self.vs = vs
        self.filesystem = fs

class AwsCredentials:
    def __init__(
            self,
            access_key_id: str,
            secret_access_key: str,
            session_token: str,
            expiration: str
    ):
        """
        NOTE: We could just return CredentialsResponseJson object, but this class makes it
        easier to adapt if the HTTP response structure changes in the future.
        We also process the string into datetime object for easier use.
        """
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.expiration_str = expiration

        # parse ISO 8601 string like "2026-01-20T22:54:09Z" of UTC (Zulu) time
        if self.expiration_str is not None:
            try:
                self.expiration = datetime.datetime.fromisoformat(self.expiration_str)
            except ValueError:
                raise ClientError("Unable to parse expiration string: %s" % self.expiration_str)
        else:
            self.expiration = None

class DraDiscoveryUrl:
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
                if rd.d.ec < len(cls.EC_RESPONSE_MAPPING):
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
                    rd.status if rd.status is not None else -1,
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

        return DeviceIdentityData(ird.d.p, ird.d.meta, ird.d.vs, ird.d.fs)

class DraCredentialsParser:

    @classmethod
    def parse_credentials_response(cls, response_str: str) -> CredentialsResponseJson:
        """
        NOTE: raises DeviceConfigError or ClientError on error
        """
        crj: CredentialsResponseJson
        try:
            crj = deserialize_dataclass(CredentialsResponseJson, json.loads(response_str))
        except json.JSONDecodeError as json_error:
            raise ClientError("Credentials JSON Parsing Error: %s" % str(json_error))

        has_error = False
        if not crj.credentials or not crj.credentials.accessKeyId or not crj.credentials.secretAccessKey or not crj.credentials.sessionToken:
            has_error = True
        if has_error:
            # try to give a meaningful error if possible
            if crj.message:
                if crj.message == 'Access Denied':
                    raise ClientError("Credentials request denied. Message: %s. Ensure that you enabled the required feature in your template." % crj.message)
                else:
                    raise ClientError("Credentials request failed. Message: %s" % crj.message)
            else:
                raise ClientError("Credentials response is missing required fields")

        return crj

class DeviceRestApi:

    def __init__(self, config: DeviceProperties, tls_credentials: Optional[DeviceTlsCredentials] = None, verbose: Optional[bool] = False):
        """
        Device REST API class to perform DRA operations like getting identity data and AWS credentials.
        Greengrass SDK NOTE: The component will not usually NOT have access to cert/key files.
        :param config: DeviceProperties needed to perform DRA operations
        :param tls_credentials: Optional TLS credentials to use for some secured HTTPS requests
        :param verbose: When true, this class will print verbose output to stdout
        """
        self.config = config
        self.tls_credentials = tls_credentials
        self.verbose = verbose

        # Cache this for use in get_aws_credentials and similar
        self.identity_response: Optional[DeviceIdentityData] = None

    def get_identity_data(self) -> DeviceIdentityData:
        try:
            if self.verbose:
                print("Requesting Discovery Data %s..." % DraDiscoveryUrl(self.config).get_api_url())
            resp = urllib.request.urlopen(urllib.request.Request(DraDiscoveryUrl(self.config).get_api_url()))
            discovery_base_url = DraDeviceInfoParser.parse_discovery_response(resp.read())

            if self.verbose:
                print("Requesting Identity Data %s..." % DraIdentityUrl(discovery_base_url).get_uid_api_url(self.config))
            resp = urllib.request.urlopen(DraIdentityUrl(discovery_base_url).get_uid_api_url(self.config))
            self.identity_response = DraDeviceInfoParser.parse_identity_response(resp.read())
            return self.identity_response

        except HTTPError as http_error:
            raise DeviceConfigError(str(http_error))

        except URLError as url_error:
            raise DeviceConfigError(str(url_error))

    def get_aws_credentials_kvs(
        self,
        client_id: Optional[str] = None, # AKA thing_name
        device_cert_path: Optional[str] = None,
        device_pkey_path: Optional[str] = None,
        server_ca_cert_path: Optional[str] = None
        ) -> AwsCredentials:
            if not self.identity_response:
                raise DeviceConfigError("Identity response is not available. Call get_identity_data() first.")
            if not self.identity_response.vs:
                raise DeviceConfigError("KVS credentials are not available in the identity response. Ensure that you enabled \"Video Streaming\" in the device template")
            return self.get_aws_credentials(
                credential_endpoint=self.identity_response.vs.url,
                client_id=client_id,
                device_cert_path=device_cert_path,
                device_pkey_path=device_pkey_path,
                server_ca_cert_path=server_ca_cert_path
            )

    def get_aws_credentials_s3(
        self,
        client_id: Optional[str] = None, # AKA thing_name
        device_cert_path: Optional[str] = None,
        device_pkey_path: Optional[str] = None,
        server_ca_cert_path: Optional[str] = None
        ) -> AwsCredentials:
            if not self.identity_response:
                raise DeviceConfigError("Identity response is not available. Call get_identity_data() first.")
            if not self.identity_response.filesystem:
                raise DeviceConfigError("Filesystem (S3) credentials are not available in the identity response. Ensure that you enabled \"Filesystem Support\" in the device template")
            return self.get_aws_credentials(
                credential_endpoint=self.identity_response.filesystem.url,
                client_id=client_id,
                device_cert_path=device_cert_path,
                device_pkey_path=device_pkey_path,
                server_ca_cert_path=server_ca_cert_path
            )


    def get_aws_credentials(
        self,
        credential_endpoint: str,
        client_id: Optional[str] = None, # AKA thing_name
        device_cert_path: Optional[str] = None,
        device_pkey_path: Optional[str] = None,
        server_ca_cert_path: Optional[str] = None,
    ) -> AwsCredentials:
        """
        Note: Call one of the appropriate get_aws_credentials_* instead, unless you need to do something custom.
        """

        if not credential_endpoint:
            raise ValueError("Credential endpoint URL is required")

        if not client_id and self.identity_response:
            client_id = self.identity_response.client_id

        if self.tls_credentials:
            if not device_cert_path:
                device_cert_path = self.tls_credentials.device_cert_path
            if not device_pkey_path:
                device_pkey_path = self.tls_credentials.device_pkey_path
            if not server_ca_cert_path:
                server_ca_cert_path = self.tls_credentials.server_ca_cert_path

        if not client_id:
            raise DeviceConfigError("Client ID (Thing Name) is required for AWS credentials request")

        if not device_cert_path or not device_pkey_path:
            raise DeviceConfigError("Device certificate and private key paths are required for AWS credentials request")

        if self.verbose:
            print("Requesting TLS credentials...")

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        what = "device cert/private key credentials"
        try:
            context.load_cert_chain(certfile=device_cert_path, keyfile=device_pkey_path)
            if server_ca_cert_path:
                what="server CA certificate"
                context.load_verify_locations(cafile=server_ca_cert_path)
        except ssl.SSLError as e:
            raise DeviceConfigError(f"Error processing {what}. Are the key and the cert matching? SSL details: {e} (errno: {e.errno}, reason: {e.reason}, strerror: {e.strerror}")
        except HTTPError as e:
            raise DeviceConfigError(f"HTTPError while processing {what}: {e}")
        except RuntimeError as e:
            raise DeviceConfigError(f"Error processing {what}. Error details: {e}")

        req = urllib.request.Request(credential_endpoint)
        req.add_header("x-amzn-iot-thingname", client_id)

        resp_str: str
        try:
            with urllib.request.urlopen(req, context=context) as response:
                resp_str = response.read()
        except ssl.SSLError as e:
            raise DeviceConfigError(f"SSLError while connecting to credentials endpoint. SSL details: {e} (errno: {e.errno}, reason: {e.reason}, strerror: {e.strerror}")
        except HTTPError as e:
            raise DeviceConfigError(f"HTTPError  while connecting to credentials endpoint: {e}")
        except URLError as e:
            raise DeviceConfigError(f"URLError while connecting to credentials endpoint: {e.reason}")
        except RuntimeError as e:
            raise DeviceConfigError(f"Error while connecting to credentials endpoint. Error details: {e}")

        # will raise DeviceConfigError or ClientError on error
        creds = DraCredentialsParser.parse_credentials_response(resp_str)
        return AwsCredentials(
            access_key_id=creds.credentials.accessKeyId,
            secret_access_key=creds.credentials.secretAccessKey,
            session_token=creds.credentials.sessionToken,
            expiration=creds.credentials.expiration
        )
