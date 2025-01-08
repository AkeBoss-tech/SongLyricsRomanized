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
        return jsonify({'error': 'No query provided'})
    
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
    if not id_value:
        return jsonify({'error': 'No query provided'})
    print(id_value)
    
    song = genius.search_song(song_id=id_value)

    if song == None:
        return jsonify({'error': 'Song not found'})
    
    print(song.title)
    print(song.lyrics)
    print(song.stats)
    print(song)
    
    return jsonify({'lyrics': song.lyrics, 'title': song.title, 'artist': song.artist, 'image_url': song.song_art_image_url, 'url': song.url, 'artist': song.primary_artist})

@app.route('/lyrics_name', methods=['GET'])
def fetch_lyrics():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'error': 'No query provided'})
    
    response = genius.search_songs(query, per_page=5)
    
    song = genius.search_song(song_id=response["hits"][0]["result"]["id"])

    if song == None:
        return jsonify({'error': 'Song not found'})
    
    print(song.title)
    print(song.lyrics)
    print(song.stats)
    print(song)
    
    return jsonify({'lyrics': song.lyrics, 'title': song.title, 'artist': song.artist, 'image_url': song.song_art_image_url, 'url': song.url, 'artist': song.primary_artist})

if __name__ == '__main__':
    app.run(debug=True)
