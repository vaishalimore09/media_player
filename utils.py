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
        {"role": "system", "content": "Format your response in JSON with the following structure: {'answer': '...', 'StartTime': '...', 'EndTime': '...'}"},
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
        
        if completion.choices and len(completion.choices) > 0:
            print(completion.choices,111)
            first_choice = completion.choices[0]
            print(first_choice,222)
            if first_choice.message and hasattr(first_choice.message, 'content'):
                message_content = first_choice.message.content
            
                if message_content:
                        try:
                            answer = None
                            message_content_lower = message_content.lower()
                            index1 = message_content_lower.find("answer")
                            print(message_content_lower,index1)
                            if index1 != -1:
                                start_index = index1 + len("answer") + 1  # Move past the ":"
                                end_index = message_content.find("\n", start_index)
                                answer = message_content[start_index:end_index].strip()
                            json_data = {
                                'answer': answer,
                            }
                            return json_data
                        except Exception as e:
                            print("Error extracting JSON data:", e)
                            return {}
            else:
                print("Message or content attribute missing in completion choice")
        else:
            print("No valid choices in completion response")

    except Exception as e:
        print("Error generating response:", e)

    return []

def generate_highlights(transcript):
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version="2023-12-01-preview",
        azure_endpoint="https://nice-vip-program.openai.azure.com"
    )
    
    try:        
        prompt = [
            {"role": "system", "content": "Extract important highlights from the above transcript. The highlights should capture key moments such as: (1) Reason for the call (2) resolution or explanation provided by agent (3) critical emotions or turning points (e.g., anger, high pitch) (4) final closing remarks but do not include closing greetings and thank you . Do not include identity and demographic details and checks done by the agent. Highlights should not overlap; ensure each highlight has distinct start and end times. Please ensure that the total duration of all selected lines in the highlight should be less than 40% of the total time duration of the transcript. Response Format: Return a JSON object named \"highlights\" containing an array of highlights. Each highlight should include \"content\" for the text of the highlight, \"offsetstarttime\" for the start time of the highlight, and \"offsetendtime\" for the end time of the highlight. The format should be: {\"content\": \"highlight content\", \"offsetstarttime\": \"start time\", \"offsetendtime\": \"end time\"}."},
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

        if completion.choices and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if first_choice.message and hasattr(first_choice.message, 'content'):
                message_content = first_choice.message.content
                                
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
        print("Error generating highlights:", e)

    return []

def generate_insights_from_transcript(transcript):
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version="2023-12-01-preview",
        azure_endpoint="https://nice-vip-program.openai.azure.com"
    )
    
    prompt = [
        {"role": "system", "content": "You are an assistant that provides detailed insights from conversations."},
        {"role": "user", "content": "Identify key themes, main points, and notable quotes. Summarize context and implications for a comprehensive understanding of the conversation."},
        {"role": "system", "content": "Identify common contact center industry insights from the given transcripts. These insights include, but are not limited to: 'did the agent greet the customer', 'did the agent ascertain the identity of the customer', 'was the agent polite and empathetic towards the customer', 'was demographic information such as name, location, or contact details verified', 'did the agent resolve the customer's issue', 'was the customer satisfied with the resolution', 'did the agent apologize if there was any inconvenience', 'did the agent follow up or confirm resolution'."},
        {"role": "user", "content": "Provide the insights along with start and end times in JSON format: {'insights': [{'insight': '...', 'offsetStartTime': '...', 'offsetEndTime': '...'}]}."},
        {"role": "user", "content": transcript}
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

        if completion.choices and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if first_choice.message and hasattr(first_choice.message, 'content'):
                message_content = first_choice.message.content
                if message_content:
                    try:
                        response_data = json.loads(message_content)
                        if 'insights' in response_data and isinstance(response_data['insights'], list):
                            print("----",response_data)
                            insights = response_data['insights']
                            print("json-----",insights)
                            return insights
                    except json.JSONDecodeError as e:
                        print("Error decoding JSON:", e)
    except Exception as e:
        print("Error generating insights:", e)
    
    return []