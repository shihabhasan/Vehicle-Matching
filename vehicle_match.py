import psycopg2
import re
from collections import Counter

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import os


def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

def execute_query(conn, query, params=None):
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error executing query:", error)
        return None

def parse_description(description):
    parsed_data = {}
    
    # Extract make
    make_match = re.search(r'\b(Volkswagen|VW|Toyota)\b', description, re.IGNORECASE)
    if make_match:
        parsed_data['make'] = 'Volkswagen' if make_match.group(1).lower() in ['volkswagen', 'vw'] else 'Toyota'
    
    # Extract model
    model_match = re.search(r'\b(Golf|Tiguan|Amarok|RAV4|Camry|86|Kluger)\b', description, re.IGNORECASE)
    if model_match:
        parsed_data['model'] = model_match.group(1)
    
    # Extract badge
    badge_match = re.search(r'\b(110TSI|132TSI|162TSI|GTI|R|GX|GT|GTS|Ascent|Black Edition)\b', description, re.IGNORECASE)
    if badge_match:
        parsed_data['badge'] = badge_match.group(1)
    
    # Extract transmission
    transmission_match = re.search(r'\b(Manual|Automatic)\b', description, re.IGNORECASE)
    if transmission_match:
        parsed_data['transmission_type'] = transmission_match.group(1)
    
    # Extract fuel type
    fuel_match = re.search(r'\b(Petrol|Diesel|Hybrid)\b', description, re.IGNORECASE)
    if fuel_match:
        parsed_data['fuel_type'] = 'Hybrid-Petrol' if fuel_match.group(1).lower() == 'hybrid' else fuel_match.group(1)
    
    # Extract drive type
    drive_match = re.search(r'\b(Front Wheel Drive|Rear Wheel Drive|Four Wheel Drive|4WD|4x4)\b', description, re.IGNORECASE)
    if drive_match:
        drive = drive_match.group(1).lower()
        if drive in ['four wheel drive', '4wd', '4x4']:
            parsed_data['drive_type'] = 'Four Wheel Drive'
        elif drive == 'front wheel drive':
            parsed_data['drive_type'] = 'Front Wheel Drive'
        elif drive == 'rear wheel drive':
            parsed_data['drive_type'] = 'Rear Wheel Drive'
    
    return parsed_data

def find_matching_vehicle(conn, parsed_data):
    conditions = []
    params = []
    
    for key, value in parsed_data.items():
        conditions.append(f"{key} ILIKE %s")
        params.append(f"%{value}%")
    
    query = f"""
    SELECT id FROM vehicle
    WHERE {' AND '.join(conditions)}
    """

    results = execute_query(conn, query, params)

    return [result[0] for result in results] if results else []

def get_most_common_vehicle(conn, vehicle_ids):
    placeholders = tuple(vehicle_ids)
    query = f"""
    SELECT vehicle_id, COUNT(*) as count
    FROM listing
    WHERE vehicle_id IN {placeholders}
    GROUP BY vehicle_id
    ORDER BY count DESC
    LIMIT 1
    """
    result = execute_query(conn, query, vehicle_ids)
    return result[0][0] if result else None

def calculate_confidence(parsed_data, matched_vehicle):
    if not matched_vehicle:
        return 0
    
    total_attributes = 6  # make, model, badge, transmission_type, fuel_type, drive_type
    matched_attributes = len(parsed_data)

    # Basic confidence based on number of matched attributes
    confidence = (matched_attributes / total_attributes) * 10
    
    # Adjust confidence based on specific attributes
    if 'make' in parsed_data and 'model' in parsed_data:
        confidence += 2
    if 'badge' in parsed_data:
        confidence += 1
    
    return min(round(confidence), 10)  # Ensure confidence doesn't exceed 10

def process_description(conn, description):
    parsed_data = parse_description(description)
    matching_vehicles = find_matching_vehicle(conn, parsed_data)
    
    if len(matching_vehicles) > 1:
        vehicle_id = get_most_common_vehicle(conn, matching_vehicles)
    elif len(matching_vehicles) == 1:
        vehicle_id = matching_vehicles[0]
    else:
        vehicle_id = None
    
    confidence = calculate_confidence(parsed_data, vehicle_id)
    
    return vehicle_id, confidence

def main():
    conn = connect_to_db()
    if not conn:
        return
    
    with open('inputs.txt', 'r') as file:
        for line in file:
            description = line.strip()
            if not description:  # Skip blank lines
                continue
            vehicle_id, confidence = process_description(conn, description)
            
            print(f"Input: {description}")
            print(f"Vehicle ID: {vehicle_id}")
            print(f"Confidence: {confidence}")
            print()
    
    conn.close()

if __name__ == "__main__":
    main()