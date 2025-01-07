from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import os

from lyricsgenius import Genius

app = Flask(__name__)
genius = Genius(os.environ.get('GENIUS_ACCESS_TOKEN'))
genius.remove_section_headers = True
genius.skip_non_songs = True

genius.search_songs("we are the champions", per_page=5)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    response = genius.search_songs(query, per_page=5)
    print(response)
    
    results = []
    for thing in response["hits"]: 
        if thing["type"] != "song": continue

        title = thing["result"]["title"]
        link = thing["result"]["url"]
        lyric_state = thing["result"]["lyrics_state"]
        id_value = thing["result"]["id"]
        image_url = thing["result"]["song_art_image_url"]

        results.append({'title': title, 'link': link, 'lyric_state': lyric_state, 'id': id_value, 'image_url': image_url})
    
    return jsonify({'results': results})

@app.route('/lyrics', methods=['GET'])
def fetch_lyrics():
    id_value = request.args.get('id', '').strip()
    
    song = genius.lyrics(song_id=id_value)
    print(song)

    if song == None:
        return jsonify({'error': 'Song not found'})
    
    return jsonify({'lyrics': song})


if __name__ == '__main__':
    app.run(debug=True)
