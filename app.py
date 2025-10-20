"""
    Language Buddy - a web application for language learning with flashcards
    Copyright (C) 2025 Andrew Niven, Lee Hoang, Nicolas Oliver, Greg Witt, Bahareh Golchin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Main application page
# 11/18/2024
#
# Execute this application with streamlit run app.py
# Run LibreTranslate in another terminal with libretranslate
#
# LibreTranslate API docs
# https://libretranslate.com/docs/
#

# Library imports
import json
import os
import genanki
import streamlit as st
from openai import OpenAI
import urllib
import requests # For LibreTranslate API calls
import base64 # for converting the audio file to base64 encoded string


# Custom module imports
# DuckDB flashcard table
from pages.duckdb_fc import flashcard_table

# =============================================================================
# Name of database
db_name_jp = "flashcards.duckdb" # For Japanese words
db_name_es = "flashcards_es.duckdb" # For Spanish words
# =============================================================================

# Prepare session state variables
if "audio" not in st.session_state: # Uploaded audio file
    st.session_state.audio = None
if "feedback" not in st.session_state: # Feedback from model
    st.session_state.feedback = None
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "table_rows" not in st.session_state: # Table rows
    st.session_state.table_rows = None
if "foreign_lang_text" not in st.session_state: # Foreign language text
    st.session_state.foreign_lang_text = None
if "english_text" not in st.session_state: # English text
    st.session_state.english_text = None
if "words" not in st.session_state:
    st.session_state.words = None
if "language" not in st.session_state:
    st.session_state.language = None
# =============================================================================


# Create an Anki deck for Japanese text
def create_anki_deck(table_rows):
    #st.table(table_rows)

    # Show cards
    for table_row in table_rows:

        # Using streamlit expander - built in
        furigana_text = table_row['furigana']
        if len(table_row['furigana']) <= 0:
            furigana_text = "N/A"

        # Add the Romaji and meaning columns
        with st.expander(f"Word: {table_row['word']} - Furigana: {furigana_text} - JLPT Level {str(table_row['level'])}"):
            st.write(f"Romaji: {table_row['romaji']}")
            st.write(f"Meaning: {table_row['meaning']}")


    if st.button("Ankify"):
        
        # Define the genanki model with fields and templates
        model = genanki.Model(
            1607392319,
            'Simple Model',
            fields=[
                {'name': 'Word'},
                {'name': 'Meaning'},
                {'name': 'Furigana'},
                {'name': 'Romaji'},
                {'name': 'Level'},
            ],
            templates=[
                {
                'name': 'Card 1',
                'qfmt': 'Word: {{Word}} - Furigana: {{Furigana}} - JLPT Level: {{Level}}',
                'afmt': '{{FrontSide}}<hr id="answer">Meaning: {{Meaning}} - Romaji: {{Romaji}}',
                },
            ]
        )

        # Create a deck with a specific ID and title
        deck = genanki.Deck(
            2059400110,
            'Japanese Words'
        )

        # For each row in the table of words, create a flashcard
        for table_row in table_rows:

            note = genanki.Note(
                model=model,
                fields=[
                    table_row['word'],
                    table_row['meaning'],
                    table_row['furigana'],
                    table_row['romaji'],
                    str(table_row['level'])
                ]
            )

            deck.add_note(note)

        # Save the deck to an anki package file
        genanki.Package(deck).write_to_file('anki.apkg')

# =============================================================================


# Given an audio file (recorded or uploaded) - have an AI model give feedback
def provide_speech_feedback(openai, speech_file, lang_name):
    # Base 64 encode the audio file (using the bytes values) and decode using utf-8
        encoded_audio = base64.b64encode(speech_file.getvalue()).decode('utf-8')

        # Read the provided audio file after encoding it
        feedback = openai.chat.completions.create(
            model="gpt-4o-audio-preview", # Required for audio input
            messages=[
                {
                    "role": "user",
                    "content": [
                            # Text to prompt the model to evaluate the audio input
                            {

                                "type": "text",
                                "text": f"Provide feedback on how good the {lang_name} pronunciation in the uploaded audio file is. If you are unable to provide pronunciation feedback, tell me if the text has grammatical errors or misspelled words."
                            },
                            # Actual audio input - must be a base64 encoded string that is decoded
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": encoded_audio,
                                    "format": "wav"
                                }
                            }
                        ]
                }
            ]
        )

        # Show the pronunciation feedback to the user
        return feedback.choices[0].message.content
# =============================================================================
# =============================================================================

# Main function
def main():

    # Set page title
    st.set_page_config(page_title="Language Buddy")


    # Create OpenAI Client
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # =============================================================================


    # Sidebar
    st.sidebar.title("Options")


    # Adjectives related to the language - for styling the app and for customizing the prompt
    lang_choice = st.sidebar.selectbox("Select a language", ["Japanese", "Spanish"])
    lang_name = lang_choice

    # Set the language name based on the user's choice.
    # When the user switches languages, the session state should be cleared
    db_table = None
    db_lang = ""
    if lang_choice == "Japanese":
        db_lang = db_name_jp
        if st.session_state.language != "Japanese":
            # Clear session state
            for key in st.session_state.keys():
                st.session_state[key] = None
            lang_name = "Japanese"
            st.session_state.language = "Japanese"
            
    elif lang_choice == "Spanish":
        db_lang = db_name_es
        if st.session_state.language != "Spanish":
            # Clear session state
            for key in st.session_state.keys():
                st.session_state[key] = None
            lang_name = "Spanish"
            st.session_state.language = "Spanish"

    # Create the DuckDB table
    db_table = flashcard_table.DuckDB_Table(db_lang)

    audio_choice = st.sidebar.radio(f"You can record or upload audio of your {lang_name} speech:", ["Record", "Upload"])

    # =============================================================================
    # DEBUG CODE for testing database functions
    view_flashcards = st.sidebar.toggle(f"Debug: View flashcards table", value=False)

    # View the table and enable debugging
    if view_flashcards == True:
        flashcards_table = None

        # Button for deleting the DB
        # WARNING - THIS IS IRREVERSIBLE!
        st.sidebar.info("Note: Deleting the DB cannot be undone!")
        if st.sidebar.button("Delete DB"):
            db_table.delete_DB()

        # Create the DB and read it
        if not os.path.exists(db_table.db_name):
            db_table.create_flashcards_DB()
            flashcards_table = db_table.read_DB()
        else:
            flashcards_table = db_table.read_DB()

        num_flashcards_tb = db_table.count_flashcards()
        num_flashcards = num_flashcards_tb['count_star()'].values
        
        # Show the table
        if st.session_state.language == "Spanish" and num_flashcards > 0:
            st.info("The word(s) in the table were machine-translated. Please double check translations with a native speaker.")
        st.table(flashcards_table)

        
        st.write(f"Number of flashcards: {num_flashcards[-1]}")


        # Add an entry
        if st.button("Add entry"):
            data = {"word": "Word1", "meaning": "Meaning1", "furigana": "Furigana1", "romaji": "Romaji1", "level": 5}
            db_table.create_DB_entry(word_params=data)
            st.rerun() # Update table in real time
        # Delete an entry
        if st.button("Delete entry"):
            db_table.delete_DB_entry(5)
            st.rerun()

    # END DEBUG CODE
    # =============================================================================
    # Informational stuff
    st.sidebar.info("Informational Links")
    # Github Link
    st.sidebar.write("You can view the source code for Language Buddy by clicking the button below.")
    st.sidebar.link_button("View Source Code", "https://github.com/GoodGuyGregory/psu-language-buddy/tree/translate")

    # LibreTranslate info
    st.sidebar.write("This project requires the Python library for the free and open source LibreTranslate machine translation API.")
    st.sidebar.write("Language Buddy is not officially associated with LibreTranslate or its products.")
    st.sidebar.link_button("LibreTranslate official website", "https://libretranslate.com/")
    st.sidebar.link_button("pypi.org link", "https://pypi.org/project/libretranslate/")
    # =============================================================================


    # Title
    st.title("Language Buddy")

    st.write(f"This web application lets you study {lang_name} in a new way! You can record or upload your dialogue and the app will generate flashcards based on words it finds. ")

    # Record or upload audio
    # Example usage here: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
    if audio_choice == "Record":
        st.session_state.audio = st.audio_input(f"Record {lang_name} audio")
    else:
        st.session_state.audio = st.file_uploader("Upload an audio file with your speech practice and check your pronunciation!", type=["mp3", "ogg", "wav"])
    
    # Variable definitions
    foreign_lang_text = None
    english_text = None
    foreign_lang_words = None
    table_rows = []

    # =============================================================================

    # If the user has uploaded or recorded audio, perform the actions below
    if st.session_state.audio != None:

        # Update session state
        #st.session_state.audio = foreign_lang_audio

        # Allow the user to playback the audio
        st.audio(st.session_state.audio)
        
        # Transcribe foreign language audio to text - 
        if st.session_state.transcription == None:
            st.session_state.transcription = openai.audio.transcriptions.create(
                file=st.session_state.audio,
                model="gpt-4o-transcribe",
            )

        # Save the transcription - this assumes the transcription succeeds
        foreign_lang_text = st.session_state.transcription.text

        # Provide speech feedback
        if st.session_state.feedback == None:
            st.session_state.feedback = provide_speech_feedback(openai, st.session_state.audio, lang_name)
        st.write(f"Feedback: {st.session_state.feedback}")


    # If there is text, show it and translate it to English
    if foreign_lang_text != None:

        # Show foreign language text
        st.write(f"{lang_name} Text: {foreign_lang_text}")

        # Translate foreign language text to English
        if st.session_state.english_text == None:
            translation = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Translate the {lang_name} sentence provided by the user to English."},
                    {
                        "role": "user",
                        "content": foreign_lang_text
                    }
                ]
            )

            # Save the translation
            st.session_state.english_text = translation.choices[0].message.content

        # Split translation into words
        if st.session_state.transcription != None:
            if st.session_state.words == None:
                st.session_state.words =  openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"Split the {lang_name} sentence provided by the user phrase into individual words, "
                                "and return a JSON Array where each element is a word. "
                                "Return only the JSON string and nothing else."
                            )
                        },
                        {
                            "role": "user",
                            "content": st.session_state.transcription.text
                        }
                    ]
                )

                # Save the words
                try:
                    # Parse content as JSON
                    foreign_lang_words = json.loads(st.session_state.words.choices[0].message.content)
                except json.JSONDecodeError:
                    
                    # Handle error
                    st.error("Error parsing JSON response from OpenAI")
    
    # Show English text if it is present
    if st.session_state.english_text:
        
        # Show English text
        st.write(f"English text: {st.session_state.english_text}")

    # If the words could be obtained, show them
    # This uses JLPT for Japanese words
    # TODO - Find an equivalent URL for analyzing Spanish words
    if lang_name == "Japanese":
        if foreign_lang_words:

            # Remove repeated words
            words = set(foreign_lang_words)

            # Partial results
            _table_rows = []

            # Iterate over words
            if st.session_state.table_rows == None:
                for word in words:

                    # Get JLPT classification
                    url = f"https://jlpt-vocab-api.vercel.app/api/words?word={urllib.parse.quote(word)}"
                    with urllib.request.urlopen(url) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode())
                            
                            # Check if data is empty, and skip the empty ones
                            if data["total"] == 0:
                                continue
                        
                            # Save the first result, ignore the rest
                            _table_rows.append(data["words"][0])

                        else:
                            st.error("Error parsing response from JLPT API")
                
                # Save the table rows
                st.session_state.table_rows = _table_rows


                # Create the Anki deck
        if st.session_state.table_rows:
            # Attempt to create the flashcards DB
            db_table.create_flashcards_DB()

            for table_row in st.session_state.table_rows:
                word = table_row['word']
                meaning = table_row['meaning']
                furigana = table_row['furigana']
                romaji = table_row['romaji']
                level = str(table_row['level'])

                # Gather data for the flashcard and insert it
                word_params = {"word": word, "meaning": meaning, "furigana": furigana, "romaji": romaji, "level": level}
                db_table.create_DB_entry(word_params)


            flashcards_table = db_table.read_DB()
            st.table(flashcards_table)

            # Create the anki deck
            create_anki_deck(st.session_state.table_rows)
        
            # Allow the user to download an anki package file
            if os.path.exists('anki.apkg'):
                with open('anki.apkg', 'rb') as file:
                    st.download_button(
                        label="Download Anki Deck",
                        data=file,
                        file_name='anki.apkg',
                        mime='application/octet-stream'
                    )
    elif lang_name == "Spanish": # Uses LibreTranslate, which performs machine translation. 
        if foreign_lang_words:

            # Remove repeated words
            words = set(foreign_lang_words)

            # Partial results
            _table_rows = []

            # Iterate over words
            if st.session_state.table_rows == None:
                for word in words:
                    url = f"http://127.0.0.1:5000/translate"

                    # Attempt to translate every word, otherwise assume LibreTranslate is not running or not installed
                    try:
                        re = requests.post(url,
                            data={
                                "q": word,
                                "source": "es",
                                "target": "en",
                            }
                        )

                        if re.status_code == 200:

                            # Save the first result, ignore the rest
                            text = re.json()
                            #st.write(text)

                            text = text["translatedText"]
                            _table_rows.append({"word": word, "meaning": text})
                        else:
                            st.error("Unable to translate words. If you are not running a local LibreTranslate server, please open a terminal and type libretranslate, then press enter.")
                        # Save the table rows
                        st.session_state.table_rows = _table_rows
                    except Exception as e:
                        st.error("It appears a local LibreTranslate server is not running or it is not installed. If it is installed with \"pip install libretranslate\", you can open another terminal and type \"libretranslate\"")
                        break # Break if a single error is found

            if st.session_state.table_rows:
                # Attempt to create the flashcards DB
                db_table.create_flashcards_DB()

                for table_row in st.session_state.table_rows:
                    word = table_row['word']
                    meaning = table_row['meaning']

                    word_params = {"word": word, "meaning": meaning}
                    db_table.create_DB_entry(word_params)

                flashcards_table = db_table.read_DB()
                st.table(flashcards_table)

        

# Call main
main()