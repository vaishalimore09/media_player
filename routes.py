# routes.py

from flask import Blueprint, jsonify, send_file, request, render_template
from utils import generate_chapters_from_transcript, search_api, generate_highlights,  generate_insights_from_transcript
import json

media_playback = Blueprint('media_playback', __name__)
search = Blueprint('search', __name__)
highlight = Blueprint('highlight', __name__)

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
            print("final chapters:-",chapters)
            insights = generate_insights_from_transcript(transcript)
            print("final insights:-", insights)
            highlights = generate_highlights(transcript)
            print("final highlights:-", highlights)
            return render_template('index.html', chapters=chapters, insights=insights, transcript=transcript, highlights=highlights, video_url=video_url)

    return "Video not found for the specified interaction ID", 404

@media_playback.route('/videos/<path:path>')
def serve_video(path):
    return send_file("videos/" + path)

@search.route('/search', methods=['GET'])
def index():
    if request.method == 'GET':
        search_query = request.args.get('searchQuery')
        transcript = request.args.get('transcript')
        if search_query is not None and len(search_query.strip()) != 0:
                    search_result = search_api(search_query, transcript)
                    if search_result:
                        return jsonify(search_result) 
    return jsonify({'error': 'Invalid search query'})