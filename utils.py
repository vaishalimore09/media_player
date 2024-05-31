# utils.py

import os
import json
from openai import AzureOpenAI

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
            {"role": "system", "content": "do not include extra information in response, just provide answer in JSON format everything as string and keep name of json as chapters:{name,offsetStartTime,offsetEndTime}"},
            {"role": "system", "content": "- time stamps should be accurate and exactly following transcript"},
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

    return []



def generate_highlights(transcript):
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    # Set up Azure OpenAI client
    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version="2023-12-01-preview",
        azure_endpoint="https://nice-vip-program.openai.azure.com"
    )
    
    try:
        prompt = [
            {"role": "system", "content": "Task: Generate a highlight video from the provided transcript. Highlights should constitute approximately 25% to 30% of the total video/transcript, capturing all important details such as the discussion topic, key points, critical emotions (e.g., anger, high pitch), and final remarks (e.g., on issue resolution). Each highlight should be concise and cover: the introduction of the problem, key discussion points, and the final review status (e.g., whether the issue was resolved or will need further attention). For videos less than 5 minutes, limit highlights to 3-4 of the most important parts only."},
            {"role": "system", "content": "Response Format: Return a JSON object named \"highlights\" containing an array of highlights. Each highlight should include \"content\" for the text of the highlight, \"offsetstarttime\" for the start time of the highlight, and \"offsetendtime\" for the end time of the highlight. The format should be: {\"content\": \"highlight content\", \"offsetstarttime\": \"start time\", \"offsetendtime\": \"end time\"}."},
            {"role": "system", "content": "- content: The text of the highlight."},
            {"role": "system", "content": "- offsetstarttime: The start time of the highlight."},
            {"role": "system", "content": "- offsetendtime: The end time of the highlight."},
            {"role": "system", "content": transcript}
        ]


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

        if completion.choices and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if first_choice.message and hasattr(first_choice.message, 'content'):
                message_content = first_choice.message.content
                # print("content:: ",message_content)
                
                if message_content:
                    message_dict = json.loads(message_content)
                    highlights_json = message_dict.get('highlights')
                    print(highlights_json)
                    return highlights_json
            else:
                print("Message or content attribute missing in completion choice")
        else:
            print("No valid choices in completion response")

    except Exception as e:
        print("Error generating chapters:", e)

    return []
