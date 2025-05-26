from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
from datetime import datetime

# add menus para outras ligas

app = Flask(__name__)
CORS(app)
clues_order_super_easy = ['club_logo', 'position', 'nationality_names', 'birthdate', 'market_value', 'best_foot', 'number']
clues_order_medium = [ 'position', 'nationality_names', 'birthdate', 'club_logo', 'market_value', 'number', 'best_foot']
clues_order_hard = [ 'best_foot', 'nationality_names', 'number', 'birthdate', 'market_value', 'position', 'club_logo']
already_known = set()
guessed_players = set()
game_difficulty = 'super_easy'
league = 'players-uefa-champions-league.csv'

def initialize_league_df(league):
    global league_df
    league_df = pd.read_csv(league) 
    league_df = league_df[league_df['market_value'] != '-'] 
    league_df = league_df[league_df['number'] != '-']
    league_df['best_foot'] = league_df['best_foot'].str.capitalize()
    league_df['birthdate'] = league_df['birthdate'].str[:-1]  
    league_df = league_df.reset_index(drop=True)
    league_df['id'] = league_df.index.astype(str)

def parse_market_value(value):
    value = value.replace('€', '')
    if 'm' in value:
        return float(value.replace('m', '')) * 1_000_000
    elif 'k' in value:
        return float(value.replace('k', '')) * 1_000
    return float(value)

def filter_by_difficulty(df, difficulty):
    df['market_value_num'] = df['market_value'].apply(parse_market_value)
    df_sorted = df.sort_values(by='market_value_num', ascending=False)
    
    if difficulty == 'super_easy':
        cutoff = int(len(df_sorted) * 0.1)
    elif difficulty == 'easy':
        cutoff = int(len(df_sorted) * 0.2)
    elif difficulty == 'medium':
        cutoff = int(len(df_sorted) * 0.5)
    else:  
        cutoff = len(df_sorted)
    
    df_filtered = df_sorted.iloc[:cutoff]
    df_filtered = df_filtered.drop(columns=['market_value_num'])
    
    return df_filtered

def choose_random_player(dataframe):
    global chosen_player
    chosen_player = dataframe.sample().iloc[0]
    print(f"Chosen player: {chosen_player['name']}")

@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('query')
    if query != '':
        suggestions = [
            {'id': pid, 'name': name, 'image': image}
            for pid, name, image in zip(league_df['id'].tolist(), league_df['name'], league_df['image'].tolist())
            if any(part.lower().startswith(query.lower()) for part in name.split()) and name not in guessed_players
        ]
    else:
        suggestions = []
    return jsonify(suggestions)  

def compare_value(guessed_player_data, chosen_player):
    guessed_value_str = guessed_player_data['market_value'].replace('€', '').replace('k', '').replace('m', '')
    chosen_value_str = chosen_player['market_value'].replace('€', '').replace('k', '').replace('m', '')
    
    guessed_value = float(guessed_value_str)
    chosen_value = float(chosen_value_str)

    guessed_units = guessed_player_data['market_value'][-1]
    chosen_units = chosen_player['market_value'][-1]

    if guessed_units == 'k' and chosen_units == 'm':
        return 'up'
    elif guessed_units == 'm' and chosen_units == 'k':
        return 'down'
    else:
        return 'up' if guessed_value <= chosen_value else 'down'
    
def create_nationlaities_set(nationality_str):
    return set(nationality_str.replace(', ', ',').split(','))

def get_age(date_string):
    birth_date = datetime.strptime(date_string, "%b %d, %Y")
    today = datetime.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def update_already_known(result):
    for key in result.keys():
        if key == 'name' or key == 'image':
            continue
        if result[key]['color'] == 'green':
            already_known.add(key)

@app.route('/player-data', methods=['GET'])
def get_player_data():
    player_id = request.args.get('id')
    guessed_player_data = league_df.loc[league_df['id'] == player_id].to_dict('records')[0]
    player_name = guessed_player_data['name']

    guessed_age = get_age(guessed_player_data['birthdate'])
    chosen_age = get_age(chosen_player['birthdate'])
    
    guessed_nationalities = create_nationlaities_set(guessed_player_data['nationality_names'])
    chosen_nationalities = create_nationlaities_set(chosen_player['nationality_names'])

    result = {
        'name': player_name, #maybe remove, not being used?
        'age': {
            'value': guessed_age,
            'color': 'green' if guessed_age == chosen_age else 'red',
            'direction': 'up' if guessed_age < chosen_age else 'down'
        },
        'club_logo': {
            'value': guessed_player_data['club_logo'],
            'color': 'green' if guessed_player_data['club_logo'] == chosen_player['club_logo'] else 'red'
        },
        'position': {
            'value': guessed_player_data['position'],
            'color': 'green' if guessed_player_data['position'] == chosen_player['position'] else 'red'
        },
        'best_foot': {
            'value': guessed_player_data['best_foot'],
            'color': 'green' if guessed_player_data['best_foot'] == chosen_player['best_foot'] else 'red'
        },
        'number': {
            'value': guessed_player_data['number'],
            'color': 'green' if guessed_player_data['number'] == chosen_player['number'] else 'red',
            'direction': 'up' if int(guessed_player_data['number']) < int(chosen_player['number']) else 'down'
        },
        'country': {
            'value': guessed_player_data['nationality_names'],
            'color': 'green' if guessed_nationalities == chosen_nationalities
                    else 'orange' if guessed_nationalities.intersection(chosen_nationalities)
                    else 'red'
        },
        'market_value': {
            'value': guessed_player_data['market_value'],
            'color': 'green' if guessed_player_data['market_value'] == chosen_player['market_value'] else 'red',
            'direction': compare_value(guessed_player_data,chosen_player)
        },
        'image': guessed_player_data['image']
    }

    guessed_players.add(player_name)
    update_already_known(result)

    is_winner = (
        result['age']['color'] == 'green' and
        result['club_logo']['color'] == 'green' and
        result['position']['color'] == 'green' and
        result['best_foot']['color'] == 'green' and
        result['number']['color'] == 'green' and
        result['country']['color'] == 'green' and
        result['market_value']['color'] == 'green'
    )
    result['is_winner'] = is_winner

    return jsonify(result)
    
@app.route('/set-difficulty', methods=['POST'])
def set_difficulty():
	data = request.get_json()
	difficulty = data.get('difficulty')
	league = data.get('league')
	if league == 'champions_league':
		league_name = 'players-uefa-champions-league.csv'
	elif league == 'laliga':
		league_name = 'players-laliga.csv'
	elif league == 'premier_league':
		league_name = 'players-premier-league.csv'
	elif league == 'liga_portugal':
		league_name = 'players-liga-portugal.csv'
	elif league == 'uefa_europe':
		league_name = 'players-europa-league.csv'
	elif league == 'uefa_conference':
		league_name = 'players-uefa-europa-conference-league.csv'
	initialize_league_df(league_name)
	game_df = filter_by_difficulty(league_df, difficulty)  
	global game_difficulty
	game_difficulty = difficulty
	already_known.clear()
	guessed_players.clear()
	choose_random_player(game_df)
	return jsonify({"success": True})

@app.route('/clue', methods=['GET'])
def get_clue():
    if game_difficulty == 'super_easy' or 'game_difficulty' == 'easy':
        order = clues_order_super_easy
    elif game_difficulty == 'medium':
        order = clues_order_medium
    else: 
        order = clues_order_hard

    clue_type = ''
    for category in order: 
        if category not in already_known:
            clue_type = category
            break
    
    if clue_type != '':
        already_known.add(clue_type)
        if clue_type == 'birthdate':
            clue = get_age(chosen_player[clue_type])
        else:
            clue = chosen_player[clue_type]
    else:
        clue = ''

    type = ''
    if clue_type == 'club_logo':
        type = 'Club'
    elif clue_type == 'position':
        type = 'Position'
    elif clue_type == 'nationality_names':
        type = 'Country'
    elif clue_type == 'birthdate':
        type = 'Age'
    elif clue_type == 'market_value':
        type = 'Market Value'
    elif clue_type == 'best_foot':
        type = 'Best Foot'
    elif clue_type == 'number':
        type = 'Number'

    result = {
        'type': type,
        'clue': clue
    } 

    return jsonify(result)

if __name__ == '__main__':
    initialize_league_df(league)
    game_df = filter_by_difficulty(league_df, game_difficulty)
    choose_random_player(game_df)
    app.run(debug=True)