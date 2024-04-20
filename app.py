import os
import json
from openai import AzureOpenAI
from flask import Flask, jsonify, send_file, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_chapters_from_transcript(transcript):
    # Load Azure OpenAI API key from environment variable
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    # Set up Azure OpenAI client
    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version="2023-12-01-preview",
        azure_endpoint="https://nice-vip-program.openai.azure.com"
    )
    
    try:
        prompt = [
            {"role": "system", "content": "Break down the entire call into a maximum of 6 chapters (for small discussions of less than 10 minutes, 3 to 4 chapters are enough) based on specific periods and key points discussed."},
            {"role": "system", "content": "include important discussions in chapters e.g at the start when the discussion is starting that time is important to check the topic of discussion. then end discussion is important to check whether the aim of discussion achieved or not and to understand ending remarks. similarly important discussions in between. "},
            {"role": "system", "content": "do not include extra information in response, just provide answer in JSON format everything as string and keep name of json as chapters:"},
            {"role": "system", "content": "- Name of the chapter"},
            {"role": "system", "content": "- offsetStartTime of the chapter"},
            {"role": "system", "content": "- offsetEndTime of the chapter"},
            {"role": "system", "content": transcript}
        ]

        # Send a completion call to generate chapters
        completion = client.chat.completions.create(
            model="vip-gpt-35-turbo-16k",
            messages=prompt,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        # print("Completion:", completion)

        # Extract chapters from completion response
        if completion.choices and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if first_choice.message and hasattr(first_choice.message, 'content'):
                message_content = first_choice.message.content
                print(message_content)
                if message_content:
                    try:
                        # Parse the JSON string into a Python dictionary
                        response_data = json.loads(message_content)
                        
                        # Check if 'chapters' key exists in the response data
                        if 'chapters' in response_data and isinstance(response_data['chapters'], list):
                            chapters = response_data['chapters']
                            return chapters
                        else:
                            print("Invalid response data format:", response_data)
                    except json.JSONDecodeError as e:
                        print("Error decoding JSON:", e)
                else:
                    print("Empty message content in completion response")
            else:
                print("Message or content attribute missing in completion choice")
        else:
            print("No valid choices in completion response")

    except Exception as e:
        print("Error generating chapters:", e)

    return []



def search_api(message, transcript):
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version="2023-12-01-preview",
        azure_endpoint="https://nice-vip-program.openai.azure.com"
    )
    
    prompt = [
        {"role": "system", "content": "Provide a concise answer and context for the following question: 'entered as message'. Search for the answer within the given transcript of a call and summarize it effectively."},
        {"role": "system", "content": "Also, include the start and end times ('offsetStartTime' and 'offsetEndTime') where the answer to the question is discussed. Include only one duration i.e. start and end offset time"},
        {"role": "system", "content": "Format your response in JSON with the following structure: {'answer': '...', 'offsetStartTime': '...', 'offsetEndTime': '...'}"},
        {"role": "system", "content": message},
        {"role": "system", "content": transcript}
    ]

    try:
        completion = client.chat.completions.create(
            model="vip-gpt-35-turbo-16k",
            messages=prompt,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        # Log completion details for debugging
        # print("Completion:", completion)

        # Extract chapters from completion response
        if completion.choices and len(completion.choices) > 0:
            print(completion.choices,111)
            first_choice = completion.choices[0]
            print(first_choice,222)
            if first_choice.message and hasattr(first_choice.message, 'content'):
                # print(first_choice.message,111)
                message_content = first_choice.message.content
                
                
                
                # return jsonify(message_content)
                if message_content:
                        try:
                            # Initialize variables to store extracted data
                            answer = None
                            offset_start_time = None
                            offset_end_time = None

                            # Convert message_content to lowercase for case-insensitive search
                            message_content_lower = message_content.lower()

                            # Find indices of target substrings
                            
                            index1 = message_content_lower.find("answer")
                            print(message_content_lower,index1)
                            index2 = message_content_lower.find("offsetstarttime")
                            index3 = message_content_lower.find("offsetendtime")

                            # Extract 'answer' if found
                            if index1 != -1:
                                start_index = index1 + len("answer") + 1  # Move past the ":"
                                end_index = message_content.find("\n", start_index)
                                answer = message_content[start_index:end_index].strip()

                            # Extract 'offsetStartTime' if found
                            if index2 != -1:
                                start_index = index2 + len("offsetstarttime") + 1  # Move past the ":"
                                end_index = message_content.find("\n", start_index)
                                offset_start_time = message_content[start_index:end_index].strip()

                            # Extract 'offsetEndTime' if found
                            if index3 != -1:
                                start_index = index3 + len("offsetendtime") + 1  # Move past the ":"
                                offset_end_time = message_content[start_index:].strip()

                            # Construct JSON object with extracted data
                            json_data = {
                                'answer': answer,
                                'offsetStartTime': offset_start_time,
                                'offsetEndTime': offset_end_time
                            }

                            return json_data

                        except Exception as e:
                            print("Error extracting JSON data:", e)
                            return {}


                # else:
                #     print("Empty message content in completion response")
            else:
                print("Message or content attribute missing in completion choice")
        else:
            print("No valid choices in completion response")

    except Exception as e:
        print("Error generating chapters:", e)

    # If no valid chapters are extracted, return an empty list or handle appropriately
    return []

# Load video data from data.json
with open('data.json', 'r') as json_file:
    video_data = json.load(json_file)

global transcript
@app.route('/media_playback', methods=['GET'])
def get_video():
    interaction_id = request.args.get('interaction_id')
    print(interaction_id)
    
    if not interaction_id:
        return "Interaction ID is required", 400

    for interaction in video_data['interactions']:
        if interaction['interaction_id'] == interaction_id:
            transcript = interaction['transcript']
            video_url = interaction['url']
            
            chapters = generate_chapters_from_transcript(transcript)

            # chapters=[{'chapter_name': 'Reconnecting', 'offset_start_time': '0:00', 'offset_end_time': '0:25'}, {'chapter_name': 'Sharing Updates', 'offset_start_time': '0:25', 'offset_end_time': '1:03'}, {'chapter_name': 'Discussing TV Show', 'offset_start_time': '1:03', 'offset_end_time': '1:35'}, {'chapter_name': 'Planning Virtual Watch Party', 'offset_start_time': '1:35', 'offset_end_time': '1:54'}, {'chapter_name': 'Checking in on Life', 'offset_start_time': '1:54', 'offset_end_time': '2:28'}, {'chapter_name': 'Ending the Call', 'offset_start_time': '2:28', 'offset_end_time': '2:55'}]

            return render_template('index.html', chapters=chapters, video_url=video_url)

    return "Video not found for the specified interaction ID", 404

@app.route('/search', methods=['GET'])
def index():
    if request.method == 'GET':
        search_query = request.args.get('searchQuery')
        # print(transcript)
        print("searchQuery:", search_query)
        if search_query is not None and len(search_query.strip()) != 0:
            for interaction in video_data['interactions']:
                # currently this is hardcoded to get transcript
                if interaction['direction'] == "INBOUND":
                    transcript = interaction['transcript']
                    # print(transcript)
                    search_result = search_api(search_query, transcript)
                    print("Search Result:", search_result)
                    if search_result:
                        print("------------------------")
                        return jsonify(search_result) 
    return jsonify({'error': 'Invalid search query'})

@app.route('/videos/<path:path>')
def serve_video(path):
    return send_file("videos/" + path)

if __name__ == '__main__':
    app.run(debug=True)
