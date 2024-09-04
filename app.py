from flask import Flask, render_template, request, jsonify, send_file
import os
import yt_dlp
import requests
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'

if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    platform = data.get('platform')
    quality = data.get('quality')

    if not url or not platform:
        return jsonify({'status': 'error', 'message': 'URL and platform are required.'}), 400

    try:
        if platform == 'youtube':
            filename = download_youtube(url, quality)
        elif platform == 'facebook':
            filename = download_facebook(url)
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported platform.'}), 400

        return jsonify({'status': 'success', 'message': 'Download complete.', 'filename': filename})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], secure_filename(filename))
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

def download_youtube(url, quality):
    ydl_opts = {
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
        'format': quality,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return os.path.basename(filename)

def download_facebook(url):
    session = requests.Session()
    response = session.get(url)
    if response.status_code != 200:
        raise Exception('Could not retrieve Facebook video.')

    html_content = response.text
    sd_video_url = find_between(html_content, 'sd_src:"', '"')
    hd_video_url = find_between(html_content, 'hd_src:"', '"')

    video_url = hd_video_url if hd_video_url else sd_video_url
    if not video_url:
        raise Exception('Could not find video URL.')

    video_response = session.get(video_url)
    if video_response.status_code != 200:
        raise Exception('Could not download video.')

    filename = os.path.join(app.config['DOWNLOAD_FOLDER'], 'facebook_video.mp4')
    with open(filename, 'wb') as f:
        f.write(video_response.content)

    return os.path.basename(filename)

def find_between(s, start, end):
    try:
        return s.split(start)[1].split(end)[0]
    except IndexError:
        return None

if __name__ == '__main__':
    app.run(debug=True)
