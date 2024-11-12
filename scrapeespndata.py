import requests
from bs4 import BeautifulSoup
import csv

# Step 1: Scrape the webpage
url = 'https://www.espn.com/nfl/scoreboard/_/week/1/year/2024/seasontype/2'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com",
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Parse the scoreboard data
scoreboard_cells = soup.find_all("div", class_="ScoreboardScoreCell")

# Step 3: Collect game data with focus on Q3 and Q4 scores
game_data = []

for cell in scoreboard_cells:
    status = cell.find("div", class_="ScoreCell__Time").text.strip()
    teams = cell.find_all("li", class_="ScoreboardScoreCell__Item")
    
    # Extract data for two teams
    if len(teams) == 2:
        team1 = teams[0]
        team2 = teams[1]

        # Get team 1 details
        team1_name = team1.find("div", class_="ScoreCell__TeamName").text.strip()
        team1_scores_by_quarter = [int(q.text.strip()) for q in team1.find_all("div", class_="ScoreboardScoreCell__Value")]
        team1_q3 = team1_scores_by_quarter[2] if len(team1_scores_by_quarter) > 2 else 0
        team1_q4 = team1_scores_by_quarter[3] if len(team1_scores_by_quarter) > 3 else 0

        # Get team 2 details
        team2_name = team2.find("div", class_="ScoreCell__TeamName").text.strip()
        team2_scores_by_quarter = [int(q.text.strip()) for q in team2.find_all("div", class_="ScoreboardScoreCell__Value")]
        team2_q3 = team2_scores_by_quarter[2] if len(team2_scores_by_quarter) > 2 else 0
        team2_q4 = team2_scores_by_quarter[3] if len(team2_scores_by_quarter) > 3 else 0

        # Calculate point differences for Q3 and Q4
        q3_difference = team1_q3 - team2_q3
        q4_difference = team1_q4 - team2_q4

        # Calculate each team's total Q3 + Q4 difference
        team1_total_difference = q3_difference + q4_difference  # For team 1
        team2_total_difference = -team1_total_difference       # For team 2 (opposite of team1's total)

        game_data.append({
            "status": status,
            "team1": team1_name,
            "team2": team2_name,
            "team1_q3": team1_q3,
            "team1_q4": team1_q4,
            "team2_q3": team2_q3,
            "team2_q4": team2_q4,
            "q3_difference": q3_difference,
            "q4_difference": q4_difference,
            "team1_total_difference": team1_total_difference,
            "team2_total_difference": team2_total_difference
        })

# Step 4: Write results to CSV
with open('game_differences.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["status", "team1", "team2", "team1_q3", "team1_q4", "team2_q3", "team2_q4", "q3_difference", "q4_difference", "team1_total_difference", "team2_total_difference"])
    writer.writeheader()
    writer.writerows(game_data)

print("Data has been written to game_differences.csv")
