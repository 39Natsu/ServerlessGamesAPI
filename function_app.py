import azure.functions as func
import logging
import requests
import json
from azure.cosmos import CosmosClient
import google.generativeai as genai
from urllib.parse import quote, unquote
import os

# Replace with your actual Google Gemini API key
genai.configure(api_key="GEMINI_API_KEY")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Initialize Cosmos DB client
client = CosmosClient(
    url="CosmosDBEndpoint",
    credential="CosmosDBKey"
)
database = client.get_database_client("GamesDB")
container = database.get_container_client("GamesContainer")

@app.route(route="Games")
def Games(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to retrieve all games from the Cosmos DB.
    """
    items = list(container.read_all_items())
    return func.HttpResponse(
        body=json.dumps(items, indent=4),  # Format JSON response for readability
        mimetype="application/json",
        status_code=200
    )

@app.route(route="getgamesbygenre/{genre}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def getgamesbygenre(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to retrieve games by genre from the Cosmos DB.
    """
    logging.info('Processing request to get games by genre.')

    genre = req.route_params.get('genre')
    if not genre:
        return func.HttpResponse("Please provide a genre in the URL path", status_code=400)

    # Decode the genre for Cosmos DB query
    decoded_genre = unquote(genre)
    logging.info(f"Decoded genre: {decoded_genre}")

    query = "SELECT * FROM c WHERE c.genre = @genre"
    parameters = [{'name': '@genre', 'value': decoded_genre}]
    
    try:
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        if not items:
            logging.error(f"No games found for genre: {decoded_genre}")
            return func.HttpResponse("No games found for the specified genre", status_code=404)

        return func.HttpResponse(
            body=json.dumps(items, indent=4),  # Format JSON response for readability
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

@app.route(route="getgamesbyyear/{year}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def getgamesbyyear(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to retrieve games by release year from the Cosmos DB.
    """
    logging.info('Processing request to get games by year.')

    year = req.route_params.get('year')  # Get the year from the route parameters

    if not year:
        return func.HttpResponse("Please provide a year in the URL path", status_code=400)

    query = f"SELECT * FROM c WHERE c.releaseyear = '{year}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    if not items:
        return func.HttpResponse("No games found for the specified year", status_code=404)

    return func.HttpResponse(
        body=json.dumps(items, indent=4),  # Format JSON response for readability
        mimetype="application/json",
        status_code=200
    )

@app.route(route="getgamesummary/{title}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def getgamesummary(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to retrieve a game summary from Google Gemini API and add it to the game details.
    """
    logging.info('Processing request to get game summary.')

    try:
        # Extract the game title from the URL and decode it
        title = req.route_params.get('title')
        if not title:
            return func.HttpResponse("Game title not provided.", status_code=400)
        
        decoded_title = unquote(title)
        logging.info(f"Decoded title: {decoded_title}")
        
        # Cosmos DB query to find the game by title
        query = "SELECT * FROM c WHERE c.title = @title"
        parameters = [{'name': '@title', 'value': decoded_title}]
        
        games = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        if not games:
            logging.error(f"No games found for title: {decoded_title}")
            return func.HttpResponse("Game not found.", status_code=404)
        
        game = games[0]  # Assuming there's only one game for the title
        
        # Generate the summary using Google Gemini
        summary = get_game_summary_from_gemini(decoded_title)
        
        # Add the generated summary to the game details
        game['generatedsummary'] = summary
        
        return func.HttpResponse(
            body=json.dumps(game, indent=4),  # Format JSON response for readability
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

def get_game_summary_from_gemini(title: str) -> str:
    """
    Function to generate a game summary using the Google Gemini API.
    """
    try:
        # Use the Gemini model to generate content
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Write a summary for the game titled '{title}'")
        
        # Log the response for debugging
        logging.info(f"Gemini API response: {response}")

        # Return the generated text
        return response.text if response else 'No summary available.'
    except Exception as e:
        logging.error(f"Exception occurred while generating summary: {str(e)}")
        return 'No summary available.'
