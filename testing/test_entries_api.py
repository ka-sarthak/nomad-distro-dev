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


# username = "anatitzhak"
# password = "Gaushle05369"
# url = "http://nomad.nanolab.dtu.dk/nomad-oasis/api/v1"

# query = {
#     "owner": "visible",
#     "query": {
#         "and": [
#             {"entry_type:all": ["DTUSputtering"]},
#         ]
#     },
#     "pagination": {
#         "page_size": 10,
#     },
#     "required": {
#         "data": "*",
#     },
# }
# entries = get_entries(query, url, username, password)
# print(f"Found {len(entries['data'])} entries.")
# with open("entries.json", "w") as f:
#     json.dump(entries["data"], f, indent=2)


if __name__ == "__main__":
    import asyncio

    # NOMAD Analysis Metadata - DO NOT EDIT
    NOMAD_ANALYSIS_ENTRY_ID = "hY5Hw09eQUWnEP1GvtOj8tcS1pl1"
    NOMAD_ANALYSIS_BASE_URL = "http://localhost:3000/nomad-oasis/api/v1"

    from nomad_analysis.utils import get_entry_data

    async def main():
        analysis = await get_entry_data(
            entry_id=NOMAD_ANALYSIS_ENTRY_ID,
            url=NOMAD_ANALYSIS_BASE_URL,
            username="sarthakdevelop",
            password="1nH@rmony01",
        )
        return analysis

    analysis = asyncio.run(main())
