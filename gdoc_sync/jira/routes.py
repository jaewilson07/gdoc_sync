# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes.ipynb.

# %% auto 0
__all__ = ['get_boards']

# %% ../../nbs/routes.ipynb 3
import urllib.parse as parse
from dataclasses import dataclass, field

import jiralibrary.client as gd
import jiralibrary.jira.auth as ja

# %% ../../nbs/routes.ipynb 5
async def get_boards(
    auth: ja.JiraAuth,
    params: dict = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    return_raw: bool = False,
):
    url = f"https://{auth.instance}/rest/agile/1.0/board"

    def arr_fn(res):
        return res.response["values"]

    res = await gd.looper(
        url=url,
        auth=auth,
        arr_fn=arr_fn,
        params=params,
        method="GET",
        debug_loop=debug_loop,
        debug_api=debug_api,
    )

    if return_raw:
        return res

    return res.response
