# routes.py

from flask import Blueprint, jsonify, send_file, request, render_template
from utils import generate_chapters_from_transcript, search_api, generate_highlights
import json

media_playback = Blueprint('media_playback', __name__)
search = Blueprint('search', __name__)
highlight = Blueprint('highlight', __name__)

# Load video data from data.json
with open('data.json', 'r') as json_file:
    video_data = json.load(json_file)

@media_playback.route('/media_playback', methods=['GET'])
def get_video():
    interaction_id = request.args.get('interaction_id')
    
    if not interaction_id:
        return "Interaction ID is required", 400

    for interaction in video_data['interactions']:
        if interaction['interaction_id'] == interaction_id:
            transcript = interaction['transcript']
            video_url = interaction['url']
    
            chapters = generate_chapters_from_transcript(transcript)
            return render_template('index2.html', chapters=chapters, video_url=video_url)

    return "Video not found for the specified interaction ID", 404

@media_playback.route('/videos/<path:path>')
def serve_video(path):
    return send_file("videos/" + path)

@search.route('/search', methods=['GET'])
def index():
    if request.method == 'GET':
        search_query = request.args.get('searchQuery')
        
        if search_query is not None and len(search_query.strip()) != 0:
            for interaction in video_data['interactions']:
                if interaction['direction'] == "INB":
                    transcript = interaction['transcript']
                    search_result = search_api(search_query, transcript)
                    if search_result:
                        return jsonify(search_result) 
    return jsonify({'error': 'Invalid search query'})

@search.route('/highlight', methods=['GET'])
def index1():
    if request.method == 'GET':
        for interaction in video_data.get('interactions', []):
            if interaction.get('direction') == "INB":
                transcript = interaction.get('transcript')
                result=generate_highlights(transcript)
                print("highlight:  --", result)
                if result:
                    if result:
                        return jsonify(result)
                    else:
                        return jsonify({'error': 'No highlights found'})
                else:
                    return jsonify({'error': 'No highlights found'})
    return jsonify({'error': 'Invalid search result'})
