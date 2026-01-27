# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> and Zackary Andraka <zackary.andraka@avnet.com> et al.

from dataclasses import dataclass, field


@dataclass
class CredentialsJson:
    accessKeyId: str = field(default=None)
    secretAccessKey: str = field(default=None)
    sessionToken: str = field(default=None)
    expiration: str = field(default=None) # ISO 8601 string like "2026-01-20T22:54:09Z" of UTC (Zulu) time

@dataclass
class CredentialsResponseJson:
    """
    Top level credentials response JSON object from a "/credentials" (or similar) endpoint
    Normally credentials will be available, but in case of error, message field will be populated.
    """
    credentials: CredentialsJson = field(default_factory=CredentialsJson)
    message: str = field(default=None)