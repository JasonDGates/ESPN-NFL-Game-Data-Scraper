import requests
from bs4 import BeautifulSoup
import csv

# Step 1: Scrape the webpage
url = 'https://www.espn.com/nfl/scoreboard/_/week/3/year/2024/seasontype/2'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com",
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Parse the scoreboard data
scoreboard_cells = soup.find_all("div", class_="ScoreboardScoreCell")

# Step 3: Collect game data in a structured format
game_data = []

for cell in scoreboard_cells:
    status = cell.find("div", class_="ScoreCell__Time").text.strip()
    teams = cell.find_all("li", class_="ScoreboardScoreCell__Item")
    
    for team in teams:
        team_name = team.find("div", class_="ScoreCell__TeamName").text.strip()
        total_score = int(team.find("div", class_="ScoreCell__Score").text.strip())
        
        # Get scores by quarter
        quarters = team.find_all("div", class_="ScoreboardScoreCell__Value")
        scores_by_quarter = [int(q.text.strip()) for q in quarters]
        
        # Make sure there are 4 quarters, add 0 if any are missing
        scores_by_quarter += [0] * (4 - len(scores_by_quarter))

        # Add data to game_data list
        game_data.append({
            "status": status,
            "team": team_name,
            "total_score": total_score,
            "q1": scores_by_quarter[0],
            "q2": scores_by_quarter[1],
            "q3": scores_by_quarter[2],
            "q4": scores_by_quarter[3],
        })

print(game_data)

# Step 4: Write data to CSV
with open('game_scores.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["status", "team", "total_score", "q1", "q2", "q3", "q4"])
    writer.writeheader()
    writer.writerows(game_data)

print("Data has been written to game_scores.csv")
