import pandas as pd
import http.client
import ssl
import json

# ================= TEAM NORMALIZATION =================
team_map = {
    "GT": "Gujarat Titans",
    "SRH": "Sunrisers Hyderabad",
    "LSG": "Lucknow Super Giants",
    "RR": "Rajasthan Royals",
    "MI": "Mumbai Indians",
    "RCB": "Royal Challengers Bengaluru",
    "CSK": "Chennai Super Kings",
    "KKR": "Kolkata Knight Riders",
    "PBKS": "Punjab Kings",
    "DC": "Delhi Capitals"
}

def normalize_team(short_team, ordered_data):
    full = team_map.get(short_team)
    if full and full in ordered_data:
        return full
    return None


# ================= API CALL =================
def get_scorecard(match_id):

    conn = http.client.HTTPSConnection(
        "cricbuzz-cricket.p.rapidapi.com",
        context=ssl._create_unverified_context()
    )

    headers = {
        'x-rapidapi-key': "e53f1ff333msh015bad1e0b37d59p13805ejsn6106d8dcc59b",
        'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    }

    conn.request("GET", f"/mcenter/v1/{match_id}/scard", headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


# ================= ORDER DATA =================
def get_ordered_data(scorecard):

    ordered = {}

    teams = []

    for inning in scorecard.get("scorecard", []):

        batting_team = inning.get("batteamname")

        teams.append(batting_team)

        ordered[batting_team] = {

            "batting": inning.get("batsman", []),

            "bowling": []  # will set later

        }

    # Assign bowlers: bowlers in an inning belong to the opposing team

    for i, inning in enumerate(scorecard.get("scorecard", [])):

        batting_team = inning.get("batteamname")

        bowling_team = teams[1 - i]  # the other team

        ordered[bowling_team]["bowling"] = inning.get("bowler", [])

    return ordered


# ================= PARSE NAME =================
def parse_name(name):

    # BOWLER → MI_B2
    if "_B" in name:
        team = name.split("_B")[0]
        index = int(name.split("_B")[1]) - 1
        return team, "BOWLER", index

    # BATSMAN → MI2
    else:
        team = ''.join([c for c in name if c.isalpha()])
        index = int(''.join([c for c in name if c.isdigit()])) - 1
        return team, "BATSMAN", index


# ================= FILTER =================
def get_valid_batsmen(bat_list):
    return [b for b in bat_list if int(b.get("balls", 0)) > 0]


def get_valid_bowlers(bowl_list):
    return [b for b in bowl_list if float(b.get("overs", 0)) > 0]


# ================= POINTS =================
def batsman_points(player):
    return int(player.get("runs", 0))


def bowler_points(player):
    return int(player.get("wickets", 0))


# ================= MAIN CALCULATION =================
def calculate_points(df, ordered_data, match_name):

    results = []

    details = []

    for participant in df["Player"].unique():

        participant_df = df[df["Player"] == participant]

        for _, row in participant_df.iterrows():

            team_short, role, index = parse_name(row["Name"])

            # 🔥 FIX: Get full team name from match
            full_team = normalize_team(team_short, ordered_data)

            if not full_team:
                continue

            # ================= BATSMAN =================
            if role == "BATSMAN":

                bat_list = ordered_data[full_team]["batting"]
                valid_batsmen = get_valid_batsmen(bat_list)

                if 0 <= index < len(valid_batsmen):
                    player = valid_batsmen[index]
                    points = batsman_points(player)
                    details.append({
                        "Participant": participant,
                        "Match": match_name,
                        "Pick": row["Name"],
                        "Player Name": player["name"],
                        "Points": points,
                        "Type": "Batting"
                    })

            # ================= BOWLER =================
            elif role == "BOWLER":

                bowl_list = ordered_data[full_team]["bowling"]
                valid_bowlers = get_valid_bowlers(bowl_list)

                if 0 <= index < len(valid_bowlers):
                    player = valid_bowlers[index]
                    points = bowler_points(player)
                    details.append({
                        "Participant": participant,
                        "Match": match_name,
                        "Pick": row["Name"],
                        "Player Name": player["name"],
                        "Points": points,
                        "Type": "Bowling"
                    })

    # Aggregate totals
    for participant in df["Player"].unique():
        participant_details = [d for d in details if d["Participant"] == participant and d["Match"] == match_name]
        bat_total = sum(d["Points"] for d in participant_details if d["Type"] == "Batting")
        bowl_total = sum(d["Points"] for d in participant_details if d["Type"] == "Bowling")
        results.append({
            "Participant": participant,
            "Match": match_name,
            "Batting Points": bat_total,
            "Bowling Points": bowl_total,
            "Total": bat_total + bowl_total
        })

    return results, details


# ================= SAVE =================
def update_output(new_results, file_name="final_output.xlsx"):

    try:
        existing_df = pd.read_excel(file_name)
    except:
        existing_df = pd.DataFrame()

    new_df = pd.DataFrame(new_results)

    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    combined_df.to_excel(file_name, index=False)


# ================= MAIN =================
def main():

    df = pd.read_excel("data/assignment.xlsx")

    matches = [
        {"id": "149618", "name": "RCB vs SRH"},
        {"id": "149629", "name": "MI vs KKR"},
        {"id": "149640", "name": "CSK vs RR"}
    ]
    all_results = []

    all_details = []

    for match in matches:

        print(f"\n🚀 Processing: {match['name']}")

        scorecard = get_scorecard(match["id"])

        ordered_data = get_ordered_data(scorecard)

        results, details = calculate_points(df, ordered_data, match["name"])

        all_results.extend(results)

        all_details.extend(details)

    update_output(all_results)

    update_output(all_details, "detailed_output.xlsx")

    print("\n✅ DONE — final_output.xlsx and detailed_output.xlsx updated")


if __name__ == "__main__":
    main()