# Main application page
# 11/18/2024
#
# Execute this application with streamlit run app.py

import os
import streamlit as st
from openai import OpenAI

def main():

    # Create OpenAI Client
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Title
    st.title("Placeholder Title")


    # Sidebar
    st.sidebar.title("Sidebar title")

    # Record audio
    # Example usage here: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
    japanese_audio = st.audio_input("Record Japanese audio")
    japanese_text = None
    english_text = None

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
    
    if english_text:
        
        # Show English text
        st.write(english_text)

        # TODO: Save the Japanese and English text to a database

    # Show tables

    st.write("Table goes here")
    st.table({'word': 'value', 'word': 'value'})
main()