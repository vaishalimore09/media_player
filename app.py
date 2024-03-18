from flask import Flask, send_file, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/video')
def get_video():
    video_id = request.args.get('id')
    video_path = f'videos/{video_id}.mp4'
    try:
        video_url = f'/video/{video_id}'  # Assuming your Flask app is hosted at the root
        return render_template('video.html', video_url=video_url)
    except FileNotFoundError:
        return "Video not found", 404

@app.route('/video/<video_id>')
def play_video(video_id):
    video_path = f'videos/{video_id}.mp4'
    try:
        return send_file(video_path, mimetype='video/mp4')
    except FileNotFoundError:
        return "Video not found", 404

if __name__ == '__main__':
    app.run(debug=True)
