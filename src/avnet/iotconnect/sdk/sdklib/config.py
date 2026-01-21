# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.
from typing import Optional
from .error import DeviceConfigError


class DeviceProperties:
    """
    This class represents the /IOTCONNECT device properties
    like device Unique ID (DUID) and account properties lke CPID, Environment etc.
    """

    def __init__(self, duid: str, cpid: str, env: str, platform: str, ):
        """
        :param platform: The IoTconnect IoT platform - Either "aws" for AWS IoTCore or "az" for Azure IoTHub
        :param env: Your account environment. You can locate this in you IoTConnect web UI at Settings -> Key Value
        :param cpid: Your account CPID (Company ID). You can locate this in you IoTConnect web UI at Settings -> Key Value
        :param duid: Your Device Unique ID
        """

        self.duid = duid
        self.cpid = cpid
        self.env = env
        self.platform = platform

    def validate(self):
        """ Format validation in cases where custom topic configuration may be needed """
        if self.duid is None or len(self.duid) < 2:
            raise DeviceConfigError('DeviceProperties: Device Unique ID (DUID) is missing')
        if self.cpid is None or len(self.cpid) < 2:
            raise DeviceConfigError('DeviceProperties: CPID value is missing')
        if self.env is None or len(self.env) < 2:
            raise DeviceConfigError('DeviceProperties: Environment value is missing')
        if self.platform not in ("aws", "az"):
            raise DeviceConfigError('DeviceProperties: Platform must be "aws" or "az"')

class DeviceTlsCredentials:
    """
    This class is used to perform mutual TLS authentication with the /IOTCONNECT platform
    for the "credentials" endpoints that are used for Kinesis Video Streaming or S3 storage access API.

    Developer Note: The client will usually validate these files. There is little benefit in doing it on the lib side (for now).
    """

    def __init__(self, device_cert_path: str, device_pkey_path: str, server_ca_cert_path: Optional[str] = None):
        """
        :param device_cert_path: Path to the device certificate file
        :param device_pkey_path: Path to the device private key file
        :param server_ca_cert_path: Path to the server CA certificate file. If not specified system CA certificates will be used.
        """

        self.device_cert_path = device_cert_path
        self.device_pkey_path = device_pkey_path
        self.server_ca_cert_path = server_ca_cert_path

