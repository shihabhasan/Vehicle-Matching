import pandas as pd
from sqlalchemy import create_engine
import os
from llm_response import llm_response

# Load environment variables from .env file into Python environment
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


def vehicle_match_llm(input_file='inputs.txt'):
    dbname=os.getenv('DB_NAME')
    user=os.getenv('DB_USER')
    password=os.getenv('DB_PASSWORD')
    host=os.getenv('DB_HOST')
    port=os.getenv('DB_PORT')
    # Create an engine
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')

    vehicle_df = pd.read_sql_query("SELECT * FROM vehicle", con=engine)
    listing_counts_df = pd.read_sql_query("SELECT vehicle_id, COUNT(*) FROM listing GROUP BY vehicle_id", con=engine)

    # Convert DataFrame to JSON
    json_vehicle = vehicle_df.to_json(orient='records')

    json_listing_count = listing_counts_df.to_json(orient='records')

    # Open the file in read mode
    with open(input_file, 'r') as file:
        # Read the entire file content
        content = file.read()


    output = llm_response(vehicle_description=content, json_vehicle=json_vehicle, json_listing_count=json_listing_count)

    return output


if __name__ == "__main__":
    
    print(vehicle_match_llm())