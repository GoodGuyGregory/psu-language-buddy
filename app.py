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

def main():

    # Create OpenAI Client
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Title
    st.title("Language Buddy")

    # Record audio
    # Example usage here: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
    japanese_audio = st.audio_input("Record Japanese audio")
    japanese_text = None
    english_text = None
    japanese_words = None
    table_rows = []

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
                        "Split the Japanese sentence provided by the user phrase into individual words, "
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
    
    if english_text:
        
        # Show English text
        st.write(english_text)

        # TODO: Save the Japanese and English text to a database

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

    if table_rows:
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

            deck = genanki.Deck(
                2059400110,
                'Japanese Words'
            )

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

            genanki.Package(deck).write_to_file('anki.apkg')
    
    if os.path.exists('anki.apkg'):
        with open('anki.apkg', 'rb') as file:
            st.download_button(
                label="Download Anki Deck",
                data=file,
                file_name='anki.apkg',
                mime='application/octet-stream'
            )

main()