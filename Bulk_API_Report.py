#!/usr/bin/env python3
import argparse
import csv
import dataclasses
import json
import requests
import os


########### DESERIALIZERS ###########
class Error(Exception):
    def __init__(self, error=None, error_description=None):
        super().__init__(error_description)
        self.errors = error


@dataclasses.dataclass
class Oauth2:
    id: str
    access_token: str
    instance_url: str
    issued_at: str
    signature: str
    token_type: str

    @property
    def buildAuthHeader(self):
        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }


@dataclasses.dataclass
class Jobs:
    done: str
    nextRecordsUrl: str
    records: list
########### END DESERIALIZERS ###########


ENDPOINTS = {
    "login": "/services/oauth2/token",
    "jobs": "/services/data/v47.0/jobs/ingest"
}

URLS = {
    "prod": "https://login.salesforce.com",
    "dev": "https://test.salesforce.com"
}


def login(host: str, endpoint: str, creds: dict) -> Oauth2:
    print(f"[*] Retrieving access token from {host + endpoint}")
    resp = requests.post(f"{host + endpoint}", params=creds)

    if resp.status_code != 200:
        raise Error(**resp.json())

    print(f"[!] Token received")
    return Oauth2(**resp.json())


def retrieve_all_bulk_api_jobs(host: str, endpoint: str, oauth2: Oauth2) -> list:
    print(f"[*] Retrieving bulk API jobs information from {host + endpoint}")

    resp = requests.get(host + endpoint, headers=oauth2.buildAuthHeader)
    if resp.status_code != 200:
        resp.raise_for_status()
    
    jobs = Jobs(**resp.json())

    records = jobs.records
    if jobs.nextRecordsUrl is not None:
        records.extend(
            retrieve_all_bulk_api_jobs(host, jobs.nextRecordsUrl, oauth2)
        )

    return records


def response_to_csv(json_data: dict) -> None:
    csv_headers = set().union(*(row.keys() for row in json_data))

    with open("Bulk API Report.csv", 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(json_data)


if __name__ == "__main__":
    oauth2_response = None

    if os.path.exists("oauth_response.json"):
        with open("oauth_response.json") as file:
            oauth2_response = Oauth2(**json.load(file))
    else:
        parser = argparse.ArgumentParser(description="Get Bulk API report")
        parser.add_argument(
            "--creds-file",
            dest="creds",
            action="store",
            required=True,
            help="Json file with user credentials and connected app client id and client secret."
        )

        parser.add_argument(
            "--env",
            "--environment",
            dest="env",
            action="store",
            choices=['prod', 'dev'],
            required=True,
            help="Environment where to pull Bulk API Report"
        )

        args = parser.parse_args()

        with open(args.creds) as file:
            oauth2_response = login(
                URLS['prod'],
                ENDPOINTS["login"],
                json.load(file)
            )

            with open('oauth_response.json', 'w') as output:
                json.dump(oauth2_response.__dict__, output)

    records = retrieve_all_bulk_api_jobs(
        oauth2_response.instance_url,
        ENDPOINTS["jobs"],
        oauth2_response
    )

    print(f"[*] Dumping {len(records)} rows to Bulk_API_Jobs.json")
    with open(f"Bulk_API_Jobs.json", 'w') as output_file:
        json.dump(records, output_file)

    print("[*] Dumping Response to a CSV file.")
    response_to_csv(records)
