import re
import json
import requests
from time import sleep

BASE_URL = 'https://poe.ninja/challenge/builds'
LEAGUE_NAME = 'sentinel'

response = requests.get(BASE_URL)
trial_league_ids = response.content.decode()
trial_league_ids = re.findall("\"name\":(.+?),\"timeMachineLabels\"", trial_league_ids)
trial_league_ids = [re.split(",", x)[1:3] for x in list(trial_league_ids)]
# get rid of leagues/events that aren't the challenge league
trial_league_ids = [x for x in list(trial_league_ids) if x[0].find(LEAGUE_NAME) != -1]
# league request versions are duplicated for some reason, but it seems to use the first for the request
trial_league_ids = trial_league_ids[0:len(trial_league_ids):2]

# split into version hash and snapshotName
versions = [x[1].removeprefix('"version":"').removesuffix('"') for x in trial_league_ids]
snapshotNames = [x[0].removeprefix('"snapshotName":"').removesuffix('"') for x in trial_league_ids]
snapshot_days = ['day-1', 'day-2', 'day-3', 'day-4', 'day-5', 'day-6']

ladder_data = {}
for (snapshotName, version) in zip(snapshotNames, versions):
    ladder_days = {}
    for snapshot_day in snapshot_days:
        # Retrieve ladder data for a specific day, league snapshot
        content_url = (
            f'https://poe.ninja/api/data/{version}/getbuildoverview?'
            f'overview={snapshotName}'
            f'&type=exp'
            f'&timemachine={snapshot_day}'
            f'&language=en'
        )
        response = requests.get(content_url)

        contents_json = response.json()

        ladder_days.update({snapshot_day: contents_json})

        # rate limit to prevent causing issues
        sleep(2)

    ladder_data.update({snapshotName: ladder_days})

with open(f'./data/{LEAGUE_NAME}_ladders.json', 'w') as f:
    json.dump(ladder_data, f, sort_keys=False)
