# Vehicle Matching System 

## Overview
This system is designed to match vehicle descriptions to specific vehicle IDs from a database. It processes natural language descriptions of vehicles and attempts to find the most likely matching vehicle in the database, providing a confidence score for each match.

## How to use
Here is a guide to run the vehicle matching program. This guide will help you set up the environment and execute the code using the provided files.

*Requirements*
First, ensure you have the necessary packages installed. You can install them using pip and the provided requirements.txt file.Install the required libraries by running `pip install -r requirements.txt`
   
Modify the .env file for the postgresql authentication & use GROQ_API_KEY which is provided by email.

*Execution*
To run the program, execute the following command in your terminal:
`python vehicle_match.py`

Also, to run the program using generative AI (LLM), use the command:
`python vehicle_match_llm.py`