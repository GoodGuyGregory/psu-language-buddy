# Main application page
# 11/18/2024
#
# Execute this application with streamlit run app.py

import json
import os
import genanki
import streamlit as st
from openai import OpenAI
import urllib

import base64 # for converting the audio file to base64 encoded string

# Create an Anki deck for Japanese text
def create_anki_deck(table_rows):
    st.table(table_rows)

    # Show cards
    for table_row in table_rows:

        # Using streamlit expander - built in
        furigana_text = table_row['furigana']
        if len(table_row['furigana']) <= 0:
            furigana_text = "N/A"
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
                                "text": f"Tell me what is in this file, then provide feedback on how good the {lang_name} pronunciation in the uploaded audio file is. If you are unable to provide pronunciation feedback, tell me if the text has grammatical errors or misspelled words."
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
        st.write(feedback.choices[0].message.content)


# Main function
def main():

    # Set page title
    st.set_page_config(page_title="Language Buddy")


    # Create OpenAI Client
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    
    # Sidebar
    st.sidebar.title("Options")

    # Adjectives related to the language - for styling the app and for customizing the prompt
    lang_name = "Japanese"
    lang_choice = st.sidebar.selectbox("Select a language", ["Japanese", "TBD1", "TBD2"])

    if lang_choice == "Japanese":
        lang_name = "Japanese"
    elif lang_choice == "TBD1":
        lang_name = "TBD1"

    audio_choice = st.sidebar.radio(f"You can record or upload audio of your {lang_name} speech:", ["Record", "Upload"])

    # Title
    st.title("Language Buddy")

    st.write(f"This web application lets you study {lang_name} in a new way! You can record or upload your dialogue and the app will generate flashcards based on words it finds. ")

    # Record or upload audio
    # Example usage here: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
    if audio_choice == "Record":
        japanese_audio = st.audio_input(f"Record {lang_name} audio")
    else:
        japanese_audio = st.file_uploader("Upload an audio file with your speech practice and check your pronunciation!", type=["mp3", "ogg", "wav"])
    
    # Variable definitions
    japanese_text = None
    english_text = None
    japanese_words = None
    table_rows = []

    # If the user has uploaded or recorded audio, perform the actions below
    if japanese_audio:

        # Allow the user to playback the audio
        st.audio(japanese_audio)
        
        # Transcribe Japanese audio to text
        transcription = openai.audio.transcriptions.create(
            file=japanese_audio,
            model="whisper-1",
        )

        # Save the transcription
        japanese_text = transcription.text

        # Provide speech feedback
        provide_speech_feedback(openai, japanese_audio, lang_name)

    # If there is text, show it and translate it to English
    if japanese_text:

        # Show Japanese text
        st.write(japanese_text)

        # Translate Japanese text to English
        translation = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Translate the sentence provided by the user to English."},
                {
                    "role": "user",
                    "content": japanese_text
                }
            ]
        )

        # Save the translation
        english_text = translation.choices[0].message.content

        # Split translation into words
        words =  openai.chat.completions.create(
            model="gpt-4o-mini",
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
                    "content": japanese_text
                }
            ]
        )

        # Save the words
        try:
            # Parse content as JSON
            japanese_words = json.loads(words.choices[0].message.content)
        except json.JSONDecodeError:
            
            # Handle error
            st.error("Error parsing JSON response from OpenAI")
    
    # Show English text if it is present
    if english_text:
        
        # Show English text
        st.write(english_text)

        # TODO: Save the Japanese and English text to a database

    # If the words could be obtained, show them
    if japanese_words:

        # Remove repeated words
        words = set(japanese_words)

        # Partial results
        _table_rows = []

        # Iterate over words
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
        table_rows = _table_rows

    # Create the Anki deck
    if table_rows:
        create_anki_deck(table_rows)
    
    # Allow the user to download an anki package file
    if os.path.exists('anki.apkg'):
        with open('anki.apkg', 'rb') as file:
            st.download_button(
                label="Download Anki Deck",
                data=file,
                file_name='anki.apkg',
                mime='application/octet-stream'
            )

main()