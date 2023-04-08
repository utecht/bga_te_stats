import json
from tqdm import tqdm


def get_option_name(options, key):
    if type(options) == list:
        if len(options) == 0:
            return ""
        return options[int(key)]["name"]
    return options[key]["name"]


def parse_options(options):
    parsed_options = {}
    for key in options:
        option = options[key]
        parsed_options[option["name"]] = get_option_name(
            option["values"], option["value"]
        )
    return parsed_options


def parse_stats(player_id, stats):
    ret = {}
    for stat_name in stats:
        stat = stats[stat_name]
        if player_id in stat["values"]:
            ret[stat_name] = stat["values"][player_id]
    return ret


def parse_player(player, results):
    parsed_player = {}
    parsed_player["score"] = player["score"]
    parsed_player["score_aux"] = player["score_aux"]
    parsed_player["gamerank"] = player["gamerank"]
    parsed_player["rank_after_game"] = player["rank_after_game"]
    parsed_player["stats"] = parse_stats(
        player["player_id"], results["stats"]["player"]
    )
    return parsed_player


def parse_players(results):
    parsed_players = []
    for player in results["player"]:
        parsed_players.append(parse_player(player, results))
    return parsed_players


def parse_table_stats(stats):
    parsed_stats = {}
    for stat_name in stats:
        stat = stats[stat_name]
        parsed_stats[stat_name] = stat["value"]
    return parsed_stats


table_data_dict = {}
with open("table_data_backup.json", "r") as f:
    table_data_dict = json.load(f)

trimmed_data = []
for game_id in tqdm(table_data_dict):
    game_data = {}
    game_data["options"] = parse_options(table_data_dict[game_id]["data"]["options"])
    game_data["players"] = parse_players(table_data_dict[game_id]["data"]["result"])
    game_data["table_stats"] = parse_table_stats(
        table_data_dict[game_id]["data"]["result"]["stats"]["table"]
    )
    trimmed_data.append(game_data)

# Function to save the table data into a file
with open("game_data.json", "w") as f:
    json.dump(trimmed_data, f, indent=2)
