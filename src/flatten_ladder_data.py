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
    user_ranks = league_day['ladderRanks']
    user_skill_modes = league_day['skillModeUse']
    skill_modes = league_day['skillModes']

    # We'd prefer to use the dpsName (vaal and alternate qualities merged together)
    # but that causes problems with our dictionary keys
    skills = [skill['name'] for skill in skills]
    skill_users = {skills[int(key)]:values for (key, values) in skill_users.items()}
    # The index of the user's name is the cumulative sum (offset) of the index of the first name in the skill
    skill_users = {key:np.cumsum(values) for (key, values) in skill_users.items()}
    skill_users = {key:[user_names[value] for value in values] for (key, values) in skill_users.items()}
    skill_users = pd.DataFrame.from_dict(skill_users, orient='index').stack().reset_index()
    skill_users.columns = ['skill_name', '_', 'character_name']
    
    user_skill_modes = {skill_modes[int(key)]['name']:values for (key, values) in user_skill_modes.items()}
    user_skill_modes = {key:np.cumsum(values) for (key, values) in user_skill_modes.items()}
    user_skill_modes = {key:[user_names[value] for value in values] for (key, values) in user_skill_modes.items()}
    user_skill_modes = pd.DataFrame.from_dict(user_skill_modes, orient='index').stack().reset_index()
    user_skill_modes.columns = ['skill_mode', '_', 'character_name']
    # users can have more than one skill mode, so let's one-hot encode it
    user_skill_modes = (user_skill_modes
        .assign(_ = 1)
        .pivot_table(columns='skill_mode', index='character_name', values='_', aggfunc=np.max)
        )

    characters_levels_ranks = pd.DataFrame.from_dict(zip(user_names, user_levels, user_ranks))
    characters_levels_ranks.columns = ['character_name', 'character_level', 'ladder rank']

    characters_skills_level = skill_users.merge(characters_levels_ranks, on='character_name')
    characters_skills_level = skill_users.merge(user_skill_modes, on='character_name')
    characters_skills_level['league'] = league_label
    characters_skills_level['day'] = day_label
    return characters_skills_level


league_days = []
for league_name in sentinel_leagues.keys():
    league_data = sentinel_leagues[league_name]
    for day_name in league_data.keys():
        day_data = league_data[day_name]
        league_days.append(
            process_league_day(day_data, league_name, day_name)
        )

league_days = pd.concat(league_days)

league_days.to_csv('./data/sentinel_ladders_processed.csv')
