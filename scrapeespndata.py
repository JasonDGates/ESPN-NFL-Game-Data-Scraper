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

# Step 3: Collect each team's Q3 + Q4 difference
team_differences = []

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
        team1_total_q3_q4 = team1_q3 + team1_q4

        # Extract team 2 details
        team2_name = team2.find("div", class_="ScoreCell__TeamName").text.strip()
        team2_scores_by_quarter = [int(q.text.strip()) for q in team2.find_all("div", class_="ScoreboardScoreCell__Value")]
        team2_q3 = team2_scores_by_quarter[2] if len(team2_scores_by_quarter) > 2 else 0
        team2_q4 = team2_scores_by_quarter[3] if len(team2_scores_by_quarter) > 3 else 0
        team2_total_q3_q4 = team2_q3 + team2_q4

        # Calculate the difference for Q3 + Q4
        difference = team1_total_q3_q4 - team2_total_q3_q4

        # Append each team's data for the CSV, with the positive or negative difference
        team_differences.append({"Team": team1_name, "Week Difference": difference})
        team_differences.append({"Team": team2_name, "Week Difference": -difference})

# Step 4: Write results to CSV with only 'Team' and 'Week Difference' columns
with open('team_differences.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["Team", "Week Difference"])
    writer.writeheader()
    writer.writerows(team_differences)

print("Data has been written to team_differences.csv")
