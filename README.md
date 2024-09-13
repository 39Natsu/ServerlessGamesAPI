# ServerlessGamesAPI
A serverless API for managing and summarizing game data using Azure Functions and Google Gemini. This project provides endpoints for retrieving games by genre, by release year, and generating summaries of games using advanced generative AI.

## Overview

This project is a serverless API built using Azure Functions and Cosmos DB, with integration to Google Gemini for generating game summaries. The API allows you to query games based on genre, year, and retrieve detailed summaries.

## Features

- Retrieve all games
- Get games by genre
- Get games by release year
- Generate game summaries using Google Gemini

## Requirements

- Python 3.9+
- Azure Functions
- Azure Cosmos DB
- Google Gemini API Key

## Installation

1. **Set up your environment**:
   - Ensure you have Python 3.9+ installed.
   - Install the necessary Python packages:
     ```bash
     pip install azure-functions azure-cosmos google-generativeai
     ```

2. **Configure API keys**:
   - Set your Google Gemini API key as an environment variable:
     ```bash
     export API_KEY=<YOUR_API_KEY>
     ```

3. **Deploy to Azure Functions**:
   - Follow the [Azure Functions deployment guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies) to deploy the code.

## API Endpoints

### Get All Games

- **Endpoint**: `/api/Games`
- **Method**: `GET`
- **Description**: Retrieves all games from the Cosmos DB.

### Get Games by Genre

- **Endpoint**: `/api/getgamesbygenre/{genre}`
- **Method**: `GET`
- **Description**: Retrieves games filtered by genre.
- **Parameters**: `genre` (URL-encoded genre name)

### Get Games by Year

- **Endpoint**: `/api/getgamesbyyear/{year}`
- **Method**: `GET`
- **Description**: Retrieves games released in a specific year.
- **Parameters**: `year` (Release year)

### Get Game Summary

- **Endpoint**: `/api/getgamesummary/{title}`
- **Method**: `GET`
- **Description**: Retrieves a summary of a game using Google Gemini.
- **Parameters**: `title` (URL-encoded game title)

## Error Handling

- **400 Bad Request**: If a required parameter is missing or invalid.
- **404 Not Found**: If no games are found for the specified criteria.
- **500 Internal Server Error**: If an unexpected error occurs.

## Contribution

Feel free to fork the repository, create issues, or submit pull requests. Please follow the code of conduct and contribution guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

