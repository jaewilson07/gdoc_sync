# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/asana/00_auth.ipynb.

# %% ../../nbs/asana/00_auth.ipynb 2
from __future__ import annotations

from dotenv import load_dotenv
import os
import json
from dataclasses import dataclass, field
from typing import List
import datetime as dt
from dateutil.parser import parse as dtu_parse
from mdutils.mdutils import MdUtils

from nbdev.showdoc import patch_to

import gdoc_sync.client as gd

# %% auto 0
__all__ = ['AsanaAuth']

# %% ../../nbs/asana/00_auth.ipynb 4
from dataclassabc import dataclassabc


@dataclassabc
class AsanaAuth(gd.Auth):
    token: str
    workspace_id: str
    base_url = "https://app.asana.com/api/1.0"
    auth_header: dict = field(repr=False, default=None)

    def __post_init__(self):
        self.generate_auth_header()

    def get_auth_token(self):
        return self.token

    def generate_auth_header(self):
        self.auth_header = {
            "authorization": f"Bearer {self.token}",
        }
        return self.auth_header
