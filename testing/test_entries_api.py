import requests
import getpass
import json


def get_access_token(
    username: str, password: str, url: str, timeout_in_sec: int = 10
) -> str:
    response = requests.get(
        url + "/auth/token",
        params={"username": username, "password": password},
        timeout=timeout_in_sec,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_entries(
    query, url: str, username: str, password: str, timeout_in_sec: int = 60
) -> list:
    access_token = get_access_token(username, password, url, timeout_in_sec)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        url + "/entries/archive/query",
        headers=headers,
        json=query,
        timeout=timeout_in_sec,
    )
    response.raise_for_status()
    return response.json()


username = "anatitzhak"
password = "Gaushle05369"
url = "http://nomad.nanolab.dtu.dk/nomad-oasis/api/v1"

query = {
    "owner": "visible",
    "query": {
        "and": [
            {"entry_type:all": ["DTUSputtering"]},
        ]
    },
    "pagination": {
        "page_size": 10,
    },
    "required": {
        "data": "*",
    },
}
entries = get_entries(query, url, username, password)
print(f"Found {len(entries['data'])} entries.")
with open("entries.json", "w") as f:
    json.dump(entries["data"], f, indent=2)
