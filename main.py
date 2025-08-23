import requests
import os

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import AzureChatOpenAI

NFL_API_KEY = os.getenv('NFL_API_KEY')
NFL_API_URL = os.getenv('NFL_API_URL')
OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
API_VERSION = os.getenv('API_VERSION')
MODEL_NAME = os.getenv('o4-mini')

def fetch_nfl_data():
	url = "https://v1.american-football.api-sports.io/leagues"
	headers = {
		'x-rapidapi-key': NFL_API_KEY,
		'x-rapidapi-host': NFL_API_URL
	}
	response = requests.get(url, headers=headers)
	response.raise_for_status()
	return response.json()

def process_nfl_data(data):
	# Example: extract relevant info
	games = data.get('response', [])
	processed = []
	for game in games:
		processed.append({
			'home_team': game['teams']['home']['name'],
			'away_team': game['teams']['away']['name'],
			'date': game['date'],
			'score_home': game['scores']['home']['total'],
			'score_away': game['scores']['away']['total'],
		})
	return processed

def get_openai_prediction(prompt):
	llm = AzureChatOpenAI(
		azure_endpoint=OPENAI_ENDPOINT,
		api_key=OPENAI_API_KEY,
		api_version=API_VERSION,
		deployment_name=MODEL_NAME
	)
	messages = [
		{"role": "system", "content": "You are an NFL prediction assistant."},
		{"role": "user", "content": prompt}
	]
	
	from langchain_core.messages import SystemMessage, HumanMessage
	lc_messages = [
		SystemMessage(content="You are an NFL prediction assistant."),
		HumanMessage(content=prompt)
	]
	response = llm.invoke(lc_messages)
	return response.content

def main():
	home_team = input("Enter the home team name: ")
	away_team = input("Enter the away team name: ")

	nfl_data = fetch_nfl_data()
	processed_data = process_nfl_data(nfl_data)

	# Find the game matching user input
	selected_game = None
	for game in processed_data:
		if (game['home_team'].lower() == home_team.lower() and
			game['away_team'].lower() == away_team.lower()):
			selected_game = game
			break

	if not selected_game:
		print("Game not found for the given teams.")
		return

	# Create a prompt for OpenAI
	prompt = (
		f"Given the following NFL game data:\n"
		f"Home Team: {selected_game['home_team']}\n"
		f"Away Team: {selected_game['away_team']}\n"
		"Predict which team is more likely to win if they play again next week."
	)
	prediction = get_openai_prediction(prompt)
	print("Prediction:", prediction)

if __name__ == "__main__":
	main()
