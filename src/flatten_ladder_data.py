import json
import pandas as pd
import numpy as np

with open('./data/sentinel_ladders.json', 'r') as f:
    sentinel_leagues = json.load(f)

def process_league_day(league_day: dict, league_label, day_label) -> pd.DataFrame:
    skills = league_day['activeSkills']
    skill_users = league_day['activeSkillUse']
    user_levels = league_day['levels']
    user_names = league_day['names']

    # We'd prefer to use the dpsName (vaal and alternate qualities merged together)
    # but that causes problems with our dictionary keys
    skills = [skill['name'] for skill in skills]
    skill_users = {skills[int(key)]:values for (key, values) in skill_users.items()}
    # The index of the user's name is the cumulative sum (offset) of the index of the first name in the skill
    skill_users = {key:np.cumsum(values) for (key, values) in skill_users.items()}
    skill_users = {key:[user_names[value] for value in values] for (key, values) in skill_users.items()}
    skill_users = pd.DataFrame.from_dict(skill_users, orient='index').stack().reset_index()
    skill_users.columns = ['skill_name', '_', 'character_name']
    characters_levels = pd.DataFrame.from_dict(zip(user_names, user_levels))
    characters_levels.columns = ['character_name', 'character_level']

    characters_skills_level = skill_users.merge(characters_levels, on='character_name')
    characters_skills_level['league'] = league_label
    characters_skills_level['day'] = day_label
    return characters_skills_level


league_days = []
for league_label in sentinel_leagues.keys():
    league = sentinel_leagues[league_label]
    for day_label in league.keys():
        day = league[day_label]
        league_days.append(
            process_league_day(day, league_label, day_label)
        )

league_days = pd.concat(league_days)

league_days.to_csv('./data/sentinel_ladders_processed.csv')
