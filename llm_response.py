from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

import os
from groq import Groq



def llm_response(vehicle_description, json_vehicle, json_listing_count):

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    model="llama3-70b-8192"

    example_input = '''
    Volkswagen Golf 110TSI Comfortline Petrol Automatic Front Wheel Drive
    VW Amarok Ultimate
    VW Golf R with engine swap from Toyota 86 GT
    '''

    example_output = '''
    Input: Volkswagen Golf 110TSI Comfortline Petrol Automatic Front Wheel Drive
    Vehicle ID: 4749339721203712
    Confidence: 9

    Input: VW Amarok Ultimate 
    Vehicle ID: 4951649860714496
    Confidence: 7

    Input: VW Golf R with engine swap from Toyota 86 GT
    Vehicle ID: 5824662093168640
    Confidence: 6
    '''


    chat_completion = client.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": f'''You are an AI assistant tasked with matching vehicle descriptions to vehicle IDs.
            The output must show the matching Vehicle ID for each description, as well as a confidence score from 0 to 10. 
            A confidence score of 0 would indicate a very uncertain match, whereas a confidence score of 10 would indicate that the match was definitely correct.
            For example, if the description did not specify the transmission type of the car, the confidence score would likely be lower than a description that did specify the transmission type (Automatic or Manual).
            If there are multiple vehicles which you find to be the most likely match, you should return the vehicle which has the most listings associated with it in the listing table.
            You must interact with the Vehicle Data and Listing Count Data. You should not need to edit the data.
            You should print the vehicle match response for each of the provided test cases - both the matching vehicle ID as well as the confidence score.
            Vehicle Data: {json_vehicle}
            Listing Count Data: {json_listing_count}
            Input: {example_input}
            Output: {example_output}
            '''
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": f"Input: {vehicle_description}, Output:",
            }
        ],
        model=model,
        temperature=0.0,
    )

    return chat_completion.choices[0].message.content