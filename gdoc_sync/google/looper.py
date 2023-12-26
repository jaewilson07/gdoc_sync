# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/google/03_looper.ipynb.

# %% auto 0
__all__ = ["GDoc_Files"]

# %% ../../nbs/google/03_looper.ipynb 2
import os

from dataclasses import dataclass, field
from typing import List

from gdoc_sync.client import get_date
import gdoc_sync.google.auth as ga
import gdoc_sync.google.drive as gd
import gdoc_sync.client as ut


from nbdev.showdoc import show_doc, patch_to


# %% ../../nbs/google/03_looper.ipynb 4
@dataclass
class GDoc_Files:
    auth: ga.GoogleAuth = field(repr=False)

    folder_id: str = None
    folder_content: List[gd.GDoc_File] = field(default_factory=lambda: [])

    service: ga.Resource = field(default=None, repr=False)
    creds: ga.Credentials = field(default=None, repr=False)

    def __post_init__(self):
        self.creds = self.auth.creds
        self.service = self.auth.generate_service(
            service_name="drive", service_version="v3"
        )


# %% ../../nbs/google/03_looper.ipynb 5
@staticmethod
@patch_to(GDoc_Files)
def _get_folder_contents(
    self: GDoc_Files, folder_id: str, return_raw: bool = False
) -> List[gd.GDoc_File]:
    """
    retrieves dictionary representation of objects in google_drive folder
    if the folder_id maps to a file will return list with one object
    """
    auth = self.auth
    page_token = None
    file_ls = []

    while True:
        res = (
            auth.service.files()
            .list(
                q=f"'{folder_id}' in parents",
                pageSize=10,
                fields="nextPageToken, files(id,webViewLink, name, mimeType,modifiedTime )",
                pageToken=page_token,
            )
            .execute()
        )

        file_ls += res.get("files", [])

        page_token = res.get("nextPageToken", None)

        if not page_token:
            break

    if return_raw:
        return file_ls

    return [gd.GDoc_File._from_json(file_obj, auth=self.auth) for file_obj in file_ls]


# %% ../../nbs/google/03_looper.ipynb 7
@patch_to(GDoc_Files)
def get_files(
    self: GDoc_Files, folder_id, file_ls=None, folder_path="", is_recursive: bool = True
):
    auth = self.auth

    if not file_ls:
        file_ls = []

    """recursive function to get files in a folder and map over files in subfolder"""

    new_files = self._get_folder_contents(folder_id=folder_id)

    file_ls += new_files

    if new_files and is_recursive:
        [
            self.get_files(
                folder_id=google_doc.doc_id,
                folder_path=os.path.join(
                    folder_path, ut.generate_file_name(google_doc.doc_name)
                ),
                file_ls=file_ls,
            )
            for google_doc in new_files
            if google_doc.mime_type == "folder"
        ]

    self.file_ls = file_ls
    return self.file_ls
