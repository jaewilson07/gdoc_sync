# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/client/client.ipynb.

# %% ../nbs/client/client.ipynb 4
from __future__ import annotations

import os
from typing import Any, Union
from dataclasses import dataclass, field
from abc import abstractmethod, ABC

from urllib.parse import urlparse

import httpx
import json

from pprint import pprint
import domolibrary_extensions.utils.utils as ut

# %% auto 0
__all__ = ['looper_offset_params', 'Auth', 'ResponseGetData', 'get_cache', 'update_cache', 'BaseError_Validation', 'BaseError',
           'get_data', 'get_data_stream', 'looper']

# %% ../nbs/client/client.ipynb 6
@dataclass
class Auth(ABC):
    """Base class for authentication"""

    @abstractmethod
    def generate_auth_header(self) -> dict:
        """Get the headers for the authentication"""
        pass

# %% ../nbs/client/client.ipynb 7
@dataclass
class ResponseGetData:
    """class for returning data from any route"""

    is_from_cache: bool
    is_success: bool

    status: int
    response: Any
    auth: Any = field(repr=False, default=None)

    def __post_init__(self):
        self.is_success = True if self.status >= 200 and self.status <= 399 else False

    @classmethod
    def _from_httpx(cls, res: httpx.Response, auth: Any = None):
        return cls(
            status=res.status_code,
            response=res.json(),
            is_success=res.is_success,
            is_from_cache=False,
            auth=auth,
        )

    @classmethod
    def _from_stream(
        cls,
        res: httpx.Response,
        content,
        auth: Any = None,
    ):
        if not res.is_success:
            content = res.json()

        return cls(
            status=res.status_code,
            response=content,
            is_success=res.is_success,
            is_from_cache=False,
            auth=auth,
        )

    @classmethod
    def _from_cache(cls, data: dict = None, auth: Any = None):
        return cls(
            status=200,
            response=data,
            is_success=True,
            is_from_cache=True,
            auth=auth,
        )

# %% ../nbs/client/client.ipynb 12
def get_cache(cache_path: str, debug_prn: bool = False) -> Union[dict, None]:
    """function for getting cached data from json file"""

    json_data = None
    ut.upsert_folder(folder_path=cache_path, debug_prn=debug_prn)

    try:
        with open(cache_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        with open(cache_path, "w+", encoding="utf-8") as file:
            pass
        json_data = None

    if json_data:
        if debug_prn:
            print(f"🚀 Using cached data in {cache_path}")

    return json_data


def update_cache(cache_path: str, data: Any, debug_prn: bool = False):
    ut.upsert_folder(cache_path)

    cache_path = ut.rename_filepath_to_match_datatype(data, cache_path)

    if debug_prn:
        print(f"updating {type(data)} content to {cache_path}")

    if isinstance(data, bytearray) or isinstance(data, bytes):
        with open(cache_path, "wb") as bf:
            return bf.write(data)

    with open(cache_path, "w+", encoding="utf-8") as fp:
        if isinstance(data, dict):
            return json.dump(data, fp)

        if isinstance(data, str):
            return fp.write(data)

# %% ../nbs/client/client.ipynb 15
class BaseError_Validation(Exception):
    def __init__(self, message):
        super().__init__(message)


class BaseError(Exception):
    def __init__(
        self, instance=None, entity_id=None, message=None, res: ResponseGetData = None
    ):
        if not (instance and message) and not res:
            raise BaseError_Validation(
                "must include instance and message or ResponseGetData class"
            )

        message = message or res.response["Message"]

        if entity_id:
            message = f"{message} for {entity_id}"

        if res:
            message = (
                f"status {res.status} || {message} in {instance or res.auth.instance}"
            )
        super().__init__(message)

# %% ../nbs/client/client.ipynb 17
def prepare_fetch(
    url: str,
    params: dict = None,
    auth: Auth = None,
    headers: dict = None,
    body: dict = None,
):
    """base function to prepare a fetch operation"""

    headers = headers or {"Accept": "application/json"}

    if auth:
        headers = {**headers, **auth.generate_auth_header()}

    return headers, url, params, body

# %% ../nbs/client/client.ipynb 18
def _generate_cache_name(url):
    uparse = urlparse(url)

    return f"./CACHE/{''.join([uparse.netloc.replace('.', '_'), uparse.path.replace('.', '_')])}.json"

# %% ../nbs/client/client.ipynb 20
async def get_data(
    url: str,
    method: str,
    cache_path: str = None,
    is_ignore_cache: bool = False,
    headers: dict = None,
    params: dict = None,
    body=None,
    auth: Auth = None,
    parent_class: str = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    client: httpx.AsyncClient = None,
    is_verify_ssl: bool = False,
) -> ResponseGetData:
    """wrapper for httpx Request library, always use with jiralibrary class"""

    cache_path = cache_path or _generate_cache_name(url)

    if not is_ignore_cache and cache_path:
        json_data = get_cache(cache_path=cache_path, debug_prn=debug_prn)

        if json_data:
            return ResponseGetData._from_cache(data=json_data, auth=auth)

    is_close_session = False if client else True
    client = client or httpx.AsyncClient(verify=is_verify_ssl)

    headers, url, params, body = prepare_fetch(
        url=url,
        params=params,
        auth=auth,
        headers=headers,
        body=body,
    )

    if debug_api:
        pprint(
            {
                "headers": headers,
                "url": url,
                "params": params,
                "body": body,
                "cache_file_path": cache_path,
                "debug_api": debug_api,
                "parent_class": parent_class,
            }
        )

    if method.upper() == "GET":
        res = await client.get(
            url=url,
            headers=headers,
            params=params,
            follow_redirects=True,
        )
    else:
        res = await getattr(client, method)(
            url=url,
            headers=headers,
            params=params,
            data=body,
        )

    if is_close_session:
        await client.aclose()

    rgd = ResponseGetData._from_httpx(res, auth=auth)

    if rgd.is_success:
        update_cache(cache_path=cache_path, data=rgd.response, debug_prn=debug_prn)

    return rgd

# %% ../nbs/client/client.ipynb 23
async def get_data_stream(
    url: str,
    cache_path: str = None,
    is_ignore_cache: bool = False,
    headers: dict = None,
    params: dict = None,
    body=None,
    auth: Auth = None,
    parent_class: str = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    client: httpx.AsyncClient = None,
    is_text: bool = False,  # if false will interpret as bytes
    is_verify_ssl: bool = False,
) -> ResponseGetData:
    """wrapper for httpx Request library, always use with jiralibrary class"""

    cache_path = cache_path or _generate_cache_name(url)

    if not is_ignore_cache and cache_path:
        json_data = get_cache(cache_path=cache_path, debug_prn=debug_prn)

        if json_data:
            return ResponseGetData._from_cache(data=json_data, auth=auth)

    is_close_session = False if client else True

    client = client or httpx.AsyncClient(verify=is_verify_ssl)

    headers, url, params, body = prepare_fetch(
        url=url,
        params=params,
        auth=auth,
        headers=headers,
        body=body,
    )

    if debug_api:
        pprint(
            {
                "headers": headers,
                "url": url,
                "params": params,
                "body": body,
                "cache_file_path": cache_path,
                "debug_api": debug_api,
                "parent_class": parent_class,
            }
        )

    content = bytearray()

    async with client.stream(
        method="GET",
        url=url,
        headers=headers,
        params=params,
        follow_redirects=True,
    ) as res:
        if is_text:
            async for chunk in res.aiter_text():
                content += chunk

        else:
            async for chunk in res.aiter_bytes():
                content += chunk

    if is_close_session:
        await client.aclose()

    rgd = ResponseGetData._from_stream(res, auth=auth, content=content)

    if rgd.is_success:
        update_cache(cache_path=cache_path, data=rgd.response, debug_prn=debug_prn)

    return rgd

# %% ../nbs/client/client.ipynb 25
looper_offset_params = {"offset": "offset", "limit": "limit"}


async def looper(
    url,
    client: httpx.AsyncClient,
    auth: Auth,
    arr_fn,
    offset=0,
    limit=50,
    params: dict = None,
    body: dict = None,
    offset_params: dict = None,
    offset_params_is_header: bool = False,
    debug_loop: bool = False,
    debug_api: bool = False,
    debug_prn: bool = False,
    method="GET",
    is_verify_ssl: bool = False,
    is_ignore_cache: bool = False,
    cache_path: str = None,
    return_raw: bool = False,  # will break the looper after the first request and ignore the array processing step.
    **kwargs
):
    offset_params = offset_params or looper_offset_params

    cache_path = cache_path or _generate_cache_name(url)

    if not is_ignore_cache and cache_path:
        json_data = get_cache(cache_path=cache_path, debug_prn=debug_prn)

        if json_data:
            return ResponseGetData._from_cache(data=json_data, auth=auth)

    final_array = []
    keep_looping = True

    while keep_looping:
        new_params = params.copy() if params else {}
        new_body = body.copy() if body else {}
        new_offset = {
            offset_params["offset"]: offset,
            offset_params["limit"]: limit,
        }
        if offset_params_is_header:
            new_params = {**new_params, **new_offset}
        else:
            new_body = {**new_body, **new_offset}

        res = await get_data(
            is_ignore_cache=True,
            auth=auth,
            url=url,
            method=method,
            params=new_params,
            debug_api=debug_api,
            debug_prn=debug_prn,
            client=client,
            is_verify_ssl=is_verify_ssl,
            body=new_body,
            **kwargs
        )

        if not res.is_success or return_raw:
            return res

        new_array = arr_fn(res)

        if debug_loop:
            print(new_params, new_body, new_array)

        if not new_array or len(new_array) == 0:
            keep_looping = False

        final_array += new_array
        offset += limit

    res.response = final_array

    if res.is_success:
        update_cache(cache_path=cache_path, data=res.response, debug_prn=debug_prn)

    return res
