# Main application page
# 11/18/2024
#
# Execute this application with streamlit run app.py

import streamlit as st

def main():

    # Title
    st.title("Placeholder Title")


    # Sidebar
    st.sidebar.title("Sidebar title")

    # Record audio
    # Example usage here: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
    japanese_audio = st.audio_input("Record Japanese audio")

    # Show Japanese text
    st.write("Japanese text goes here")

    # Allow the user to playback the audio
    if japanese_audio:
        st.audio(japanese_audio)

    # TODO: Convert Japanese audio to text

    # Show English text
    st.write("English text goes here")

    # Show tables

    st.write("Table goes here")
    st.table({'word': 'value', 'word': 'value'})
main()