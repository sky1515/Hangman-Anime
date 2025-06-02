from flask import Flask, render_template, request, session, redirect, url_for
import requests
import random

app = Flask(__name__)
app.secret_key = 'test_env'

API_URL = 'https://api.jikan.moe/v4/anime'

def get_random_word():
    response = requests.get(API_URL)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        total_pages = response.json()["pagination"]["last_visible_page"]
        random_page = random.randint(1,total_pages)
        response = requests.get(f"https://api.jikan.moe/v4/anime?page={random_page}")
        if response.status_code == 200:
            anime_list = response.json()["data"]
            random_anime = random.choice(anime_list)
            title = random_anime.get("title", "UNKNOWN TITLE")
            image_url = random_anime.get("images",{}).get("webp",{}).get("image_url", url_for('static', filename='images/8.svg'))
            print("Random anime: ", image_url)
            return title, image_url
        
    return None, None

# Main page
@app.route('/')
def index():
    if 'word' not in session:
        rand_word, image_url = get_random_word()
        session['word'] = rand_word.upper()
        session['anime_image']= image_url
        session['guesses']=[]
        session['misses'] = 0
        session['message'] = ''
    word_display =''
    for letter in session['word']:
        if letter == ' ':
            word_display+='    '
        else:
            if letter.upper() in session['guesses']:
                word_display+=letter.upper()
            else:
                word_display+=' _ '
    return render_template('index.html', word_display=word_display, guesses=session['guesses'], misses=session['misses'], message=session.get('message', ''), word=session['word'], anime_image= session.get('anime_image', None))

# Reset Game
@app.route('/reset')
def reset():
    session.pop('word', None)
    session.pop('guesses', None)
    session.pop('misses', None)
    session.pop('message', None)
    return redirect(url_for('index'))

# Guesses
@app.route('/guess', methods=['POST'])
def guess():
    guess = request.form.get('guess').upper()
    print("Guess: ", guess)
    if guess not in session['guesses']:
        session['guesses'].append(guess)
        if guess in session['word']:
            session['message'] = f"Correct guess! '{guess}' is in the word."
        else:
            session['misses'] += 1
            session['message'] = f"Incorrect! '{guess}' is not in the word."
    else:
        session['message'] = f"You already guessed '{guess}'."
    return redirect(url_for('index'))
    


if __name__ == '__main__':
    app.run(debug=True)
    