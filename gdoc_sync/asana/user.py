# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/asana/01_user.ipynb.

# %% ../../nbs/asana/01_user.ipynb 2
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from nbdev.showdoc import patch_to

import gdoc_sync.asana.auth as aa
import gdoc_sync.client as gd

# %% auto 0
__all__ = ['AsanaUser']

# %% ../../nbs/asana/01_user.ipynb 3
@dataclass
class AsanaUser:
    id: str
    name: str
    auth: aa.AsanaAuth = field(repr=False)
    resource_type: str = field(repr=False)
    email: str = None

    @classmethod
    def _from_json(cls, obj, auth: aa.AsanaAuth):
        return cls(
            id=obj["gid"],
            name=obj["name"],
            email=obj.get("email"),
            resource_type=obj["resource_type"],
            auth=auth,
        )

# %% ../../nbs/asana/01_user.ipynb 6
@patch_to(AsanaUser, cls_method=True)
async def get_by_id(
    cls,
    user_id: str,
    auth: aa.AsanaAuth,
    debug_api: bool = False,
    return_raw: bool = False,
) -> AsanaUser:
    """Get a user by ID"""
    url = f"{auth.base_url}/users/{user_id}"

    res = await gd.get_data(url, auth=auth, method="GET", debug_api=debug_api)

    if return_raw:
        return res

    return cls._from_json(res.response["data"], auth=auth)
