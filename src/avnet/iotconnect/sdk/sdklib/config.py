# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

from .error import DeviceConfigError



class DeviceProperties:
    """
    This class represents the /IOTCONNECT device properties
    like device Unique ID (DUID) and account properties lke CPID, Environment etc.
    """

    def __init__(self, duid: str, cpid: str, env: str, platform: str):
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
