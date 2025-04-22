# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

class DeviceConfigError(RuntimeError):
    def __init__(self, message: str):
        self.msg = message
        super().__init__(message)

class ClientError(RuntimeError):
    def __init__(self, message: str):
        self.msg = message
        super().__init__(message)

class C2DDecodeError(RuntimeError):
    def __init__(self, message: str):
        self.msg = message
        super().__init__(message)