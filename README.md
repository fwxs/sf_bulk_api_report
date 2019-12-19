# Bulk API report
Retrieve a CSV file with information of an org's Bulk API jobs.

## Credentials file format

``` json
{
    "client_id": "<client id>",
    "client_secret": "<client_secret>",
    "username": "<username>",
    "password": "<password followed by user token>",
    "grant_type": "password"
}
```


## Usage

User profile must be have:
- **_API enable_** checked
- **_Manage Data Integrations_** checked

Otherwise, when trying to get data from _/services/data/vXX.X/jobs/ingest_, you will get a **NOT FOUND** Error

```
$ python Bulk_API_Report.py --creds-file [Json creds file] --env [prod or dev]

[*] Retrieving access token from https://[login|test].salesforce.com/services/oauth2/token
[!] Token received
[*] Retrieving bulk API jobs information from <instance url>
[*] Dumping [amount of rows retrieved] jobs to Bulk_API_Jobs.json
[*] Dumping data to a CSV file.
```
