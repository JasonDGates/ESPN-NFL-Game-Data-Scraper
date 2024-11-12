import requests
from bs4 import BeautifulSoup
import csv

# Set the year, base URL, and specify the number of weeks to check
year = 2024
base_url = 'https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{year}/seasontype/2'
weeks_to_check = 10  # Set this to the number of weeks you want to scrape

# Dictionary to store data with each team as a key
team_data = {}

# Loop through each week
for week in range(1, weeks_to_check + 1):
    url = base_url.format(week=week, year=year)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com",
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all teams on a bye for the week
    bye_week_teams = []
    bye_section = soup.find("section", class_="Card ScoreboardByeWeek")
    if bye_section:
        bye_team_elements = bye_section.find_all("a", class_="AnchorLink")
        bye_week_teams = [team.text.strip() for team in bye_team_elements]

    # Assign 0 for all teams on a bye durnig the week
    for team in bye_week_teams:
        if team not in team_data:
            team_data[team] = {"weekly_diffs": [], "total_diff": 0}
        team_data[team]["weekly_diffs"].append(0)
    
    # Find all score cells for the current week
    scoreboard_cells = soup.find_all("div", class_="ScoreboardScoreCell")
    
    for cell in scoreboard_cells:
        status = cell.find("div", class_="ScoreCell__Time").text.strip()
        teams = cell.find_all("li", class_="ScoreboardScoreCell__Item")
        
        if len(teams) == 2:
            team1 = teams[0]
            team2 = teams[1]
            
            # Extract team 1 details
            team1_name = team1.find("div", class_="ScoreCell__TeamName").text.strip()
            team1_scores_by_quarter = [int(q.text.strip()) for q in team1.find_all("div", class_="ScoreboardScoreCell__Value")]
            team1_q3 = team1_scores_by_quarter[2] if len(team1_scores_by_quarter) > 2 else 0
            team1_q4 = team1_scores_by_quarter[3] if len(team1_scores_by_quarter) > 3 else 0
            team1_ot = team1_scores_by_quarter[4] if len(team1_scores_by_quarter) > 4 else 0
            team1_total_q3_q4_ot = team1_q3 + team1_q4 + team1_ot

            # Extract team 2 details
            team2_name = team2.find("div", class_="ScoreCell__TeamName").text.strip()
            team2_scores_by_quarter = [int(q.text.strip()) for q in team2.find_all("div", class_="ScoreboardScoreCell__Value")]
            team2_q3 = team2_scores_by_quarter[2] if len(team2_scores_by_quarter) > 2 else 0
            team2_q4 = team2_scores_by_quarter[3] if len(team2_scores_by_quarter) > 3 else 0
            team2_ot = team2_scores_by_quarter[4] if len(team2_scores_by_quarter) > 4 else 0
            team2_total_q3_q4_ot = team2_q3 + team2_q4 + team2_ot

            # Calculate the difference
            difference = team1_total_q3_q4_ot - team2_total_q3_q4_ot
            
            # Initialize team data and update weekly differences
            if team1_name not in team_data:
                team_data[team1_name] = {"weekly_diffs": [], "total_diff": 0}
            if team2_name not in team_data:
                team_data[team2_name] = {"weekly_diffs": [], "total_diff": 0}

            # Update weekly differences and total difference
            team_data[team1_name]["weekly_diffs"].append(difference)
            team_data[team1_name]["total_diff"] += difference

            team_data[team2_name]["weekly_diffs"].append(-difference)
            team_data[team2_name]["total_diff"] += -difference

# Step 4: Write to CSV with "Team", "Week 1", ..., "Week N", and "Total Difference" columns
fieldnames = ["Team"] + [f"Week {i+1}" for i in range(weeks_to_check)] + ["Total Difference"]

with open('weekly_team_differences_with_totals.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(fieldnames)
    
    # Write each team's data
    for team, data in team_data.items():
        # Fill in missing weeks with 0 if a team has fewer entries than the number of weeks checked
        while len(data["weekly_diffs"]) < weeks_to_check:
            data["weekly_diffs"].append(0)
        
        # Write the row with team name, weekly differences, and total difference
        writer.writerow([team] + data["weekly_diffs"] + [data["total_diff"]])

print("Data has been written to weekly_team_differences_with_totals.csv")
