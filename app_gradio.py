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

# Main application page (GRADIO VERSION)
# 11/7/2025
#
# Execute this application with 
# 
# gradio app_gradio.py
#
# Run LibreTranslate in another terminal with 
# 
# libretranslate
#
# LibreTranslate API docs
# https://libretranslate.com/docs/
#
# Gradio docs
# https://www.gradio.app/docs/gradio/interface
# =============================================================================

# Library imports
import json                 # Managing JSON objects
import os                   # Managing folders
import genanki              # For all anki stuff
import streamlit as st      # For running this web application
from openai import OpenAI   # For OpenAI model calls
import urllib               # For parsing URL data
import requests             # For LibreTranslate API calls
import base64               # for converting the audio file to base64 encoded string
import gradio as gr         # For creating the Gradio UI

# Custom module imports
# DuckDB flashcard table
from pages.duckdb_fc import flashcard_table

# =============================================================================
# Variables

# Languages to use
languages = ['Japanese', 'Spanish']

# =============================================================================

# Main UI for the application
with gr.Blocks(title="Language Buddy", analytics_enabled=False) as demo:

    # Tab for recording or uploading a speech sample to have it analyzed.
    # TODO - add callback functions
    with gr.Tab("Record speech"):
        gr.Markdown("# Language Buddy")

        gr.Markdown(f"This web application lets you study languages in a new way! You can record or upload your dialogue and the app will generate flashcards based on words it finds. ")


        with gr.Row(equal_height=True):

            # Language selection dropdown menu
            selected_lang = gr.Dropdown(
                languages, 
                label="Language", 
                interactive=True
            )

            # Audio record widget
            with gr.Column(scale=3):
                audio = gr.Audio(
                    sources=['microphone', 'upload'], 
                    show_download_button=True, 
                    show_share_button=False
                )

    # Tab for viewing flashcards by language
    with gr.Tab("View flashcards"):
        gr.Markdown("# Flashcards Table")

        # TODO - add callback functions
    
    # Sidebar
    with gr.Sidebar(position="left"):

        # Informational stuff
        # Reused from the streamlit version
        gr.Markdown("# Informational Links")
        # Github Link
        gr.Markdown("You can view the source code for Language Buddy by clicking the button below.")
        gr.Markdown("View Source Code: [Repo Link](https://github.com/GoodGuyGregory/psu-language-buddy/tree/bugfixing)")

        # LibreTranslate info
        gr.Markdown("This project requires the Python library for the free and open source LibreTranslate machine translation API.")
        gr.Markdown("Language Buddy is not officially associated with LibreTranslate or its products.")
        gr.Markdown("LibreTranslate official website: [Website](https://libretranslate.com/)")
        gr.Markdown("pypi.org link: [pypi.org](https://pypi.org/project/libretranslate/)")

# =============================================================================
# Launch the app and open a browser window automatically
if __name__ == "__main__":
    demo.launch(
        inbrowser=True,
        share=False,
    )