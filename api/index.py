from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

CORS_PROXY = ""

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    search_url = f"https://www.google.com/search?q=site:genius.com+{query}"
    response = requests.get(CORS_PROXY + search_url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch search results'}), 500
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    genius_links = [link for link in links if "https://genius.com" in link]

    characters = "%&"

    # ignore all characters after a % or & in the URL
    for i in range(len(genius_links)):
        for char in characters:
            if char in genius_links[i]:
                genius_links[i] = genius_links[i].split(char)[0]
    
    if not genius_links:
        return jsonify({'results': []})
    
    results = []
    for link in genius_links[:3]:  # Limit to 3 results
        song_title = decode_title(link)
        results.append({'title': song_title, 'url': link})
    
    return jsonify({'results': results})

@app.route('/lyrics', methods=['GET'])
def fetch_lyrics():

    url = request.args.get('url', '').strip()
    print("URL", url)
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    response = requests.get(CORS_PROXY + url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch lyrics'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    lyrics_containers = soup.find_all('div', {'data-lyrics-container': 'true'})
    
    if not lyrics_containers:
        return jsonify({'lyrics': 'Lyrics not found.'})
    
    lyrics = []
    for container in lyrics_containers:
        print("CONTAINER", container)
        for br in container.find_all("br"):
            br.replace_with("\n")
        lyrics.append(container.get_text().strip() + '\n')
    
    return jsonify({'lyrics': '\n'.join(lyrics)})

def decode_title(link):
    song_title = link.split('/')[-1].replace('-', ' ').replace('.html', '')
    return ' '.join(word.capitalize() for word in song_title.split())

if __name__ == '__main__':
    app.run(debug=True)
