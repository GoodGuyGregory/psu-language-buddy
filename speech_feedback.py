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

# Test app for providing pronunciation feedback to the user
# 4/11/2025
#
# Execute this application with streamlit run speech_feedback.py
#
# References: https://platform.openai.com/docs/guides/audio?example=audio-in&lang=python

import streamlit as st
from openai import OpenAI
import os 
import base64 # for converting the audio file to base64 encoded string

def main():

    # Create OpenAI Client
    openai = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    # Title
    st.title("Speech feedback")

    st.write("This web application lets you upload an audio file and check how good your pronunciation is. ")
    st.write("NOTE: Sometimes, the app will not be able to read the audio file. ")

    # User can upload an audio file
    speech_file = st.file_uploader("Upload an audio file with your speech practice and check your pronunciation!")

    # Check if the provided audio file is valid
    if speech_file is not None:

        # Allow the user to listen to the file they uploaded
        st.audio(speech_file)

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
                                "text": "Tell me what is in this file, then provide feedback on how good the Japanese pronunciation in the uploaded audio file is. If you are unable to provide pronunciation feedback, tell me if the text has grammatical errors or misspelled words."
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



# Run the app
main()

