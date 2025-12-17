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
import json                     # Managing JSON objects - Not used right now
import os                       # Managing folders
import genanki                  # For all anki stuff - Not used right now
from openai import OpenAI       # For OpenAI model calls
import urllib                   # For parsing URL data - Not used right now
import requests                 # For LibreTranslate API calls - Not used right now
import base64                   # for converting the audio file to base64 encoded string
import gradio as gr             # For creating the Gradio UI
from dotenv import load_dotenv  # For loading environment variables - see https://pypi.org/project/python-dotenv/

# Other imports
import io                                                       # For working with byte/audio inputs
from agents import Agent, Runner                                # Agentic AI stuff
from agents.extensions.models.litellm_model import LitellmModel # For using other models with the agent

# Custom module imports
# DuckDB flashcard table
from pages.duckdb_fc import flashcard_table
# =============================================================================
# Load the API key using dotenv
load_dotenv(override=True)

oai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# If the key cannot be found, show an error message
if not oai_api_key:
    print("No OpenAI API key was found. Please set an OpenAI API key in your .env file and reload the application.")

if not anthropic_api_key:
    print("No Anthropic API key was found. Please set an Anthropic API key in your .env file and reload the application.")

# =============================================================================
# Variables

# Languages to use
languages = ['Japanese', 'Spanish']

# Models to select
model_list = ['gpt-4.1', 'gpt-4o', "claude-sonnet-4.5", 'test model']

# =============================================================================
# Agentic AI definitions
# https://openai.github.io/openai-agents-python/quickstart/
# This agent is hardcoded to use gpt-4.1.
translation_agent_openai = Agent(
    name="Translation Agent",
    instructions="You translate Japanese words to English. Provide your response as follows: <English Translation of Word>\n<Explain how you arrived at the translation.>",
    model="gpt-4.1"
)

# This is another Agent that does the same thing as above but with GPT-4o
translation_agent_openai_4o = Agent(
    name="Translation Agent",
    instructions="You translate Japanese words to English. Provide your response as follows: <English Translation of Word>\n<Explain how you arrived at the translation.>",
    model="gpt-4o"
)

# This is another Agent that does the same thing as above but with an Anthropic model
#https://openai.github.io/openai-agents-python/models/litellm/
translation_agent_claude = Agent(
    name="Translation Agent",
    instructions="You translate Japanese words to English. Provide your response as follows: <English Translation of Word>\n<Explain how you arrived at the translation.>",
    model=LitellmModel(model="anthropic/claude-sonnet-4-5-20250929", api_key=anthropic_api_key)
)

# Run the agent above to translate a word using an agent
# Please keep in mind that the user needs to double check translations
async def run_translation_agent(word: str, model: str):
    selected_agent = None
    # Execute the agent
    if model == "gpt-4.1": # If the user selected gpt-4.1, run this specific agent
        selected_agent = translation_agent_openai
    elif model == "gpt-4o":
        selected_agent = translation_agent_openai_4o
    elif model == "claude-sonnet-4.5":
        selected_agent = translation_agent_claude
    else: # Unsupported model
        return gr.Textbox("ERROR: This model is not supported. Please try a different model.", label="ERROR", visible=True)
    
    # Supported model - print the final output
    result = await Runner.run(
        selected_agent, 
        f"What is the English meaning of {word}?"
    )
    print(result.final_output)
    return gr.Textbox(result.final_output, label="Here is the translation. Please double-check the result with a native speaker.", visible=True)


# =============================================================================
# Callback functions to load the dataframe
def load_fc_table() -> gr.Dataframe:
    """
    Load a flashcard table.

    Parameters:
        None

    Returns:
        a Gradio dataframe object 
    """
    db = flashcard_table.DuckDB_Table("flashcards.duckdb") # Flashcard table with Japanese words
    res = db.read_DB().df() # Read the DB and convert it to a dataframe
    return gr.Dataframe(res), res # Return a gradio DF object

# =============================================================================

# Given an audio file (recorded or uploaded) - have an AI model give feedback
# Only text is returned. 
def provide_speech_feedback(
        openai: OpenAI, 
        speech_file: io.BufferedReader, 
        lang_name: str
        ):
    # Base 64 encode the audio file (using the bytes values) and decode using utf-8
        encoded_audio = base64.b64encode(speech_file).decode('utf-8')

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



# For the record/upload speech tab
def process_audio_file(file, lang_name):
    """
    Process an audio file uploaded or recorded by the user.

    """
    # TODO

    # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.tobytes.html
    # Read the file using Python's file open library
    # https://platform.openai.com/docs/guides/speech-to-text#quickstart
    audio_file_bytes = open(file, "rb")

    # Create the OpenAI client
    openai = OpenAI(api_key=oai_api_key)

    # Transcribe the text
    transcribed_text = "Placeholder"
    try:
        transcription = openai.audio.transcriptions.create(
            file=audio_file_bytes,
            model="gpt-4o-transcribe",
        )
        transcribed_text = transcription.text
    except Exception as e:
        print(e)
        transcribed_text = f"Unable to generate transcription. Please try again.\n\n{e}"

    # Provide feedback
    # Not yet implemented
    feedback_text = "Feedback placeholder"
    # try:
    #     feedback_text = provide_speech_feedback(openai, audio_file_bytes.read(), lang_name)
    # except Exception as e:
    #     print(e)
    #     feedback_text = f"Sorry, there was an error generating feedback. Please try again.\n\n{e}"

    cleaned_filename = file.split("\\")[-1]

    return gr.Textbox(f"{cleaned_filename}", label="Filename", interactive=False, visible=True), gr.Textbox(f"{transcribed_text}", label="Transcription", interactive=False, visible=True), gr.Textbox(f"{feedback_text}", label="Feedback", interactive=False, visible=True)



# =============================================================================
# Main UI for the application
with gr.Blocks(title="Language Buddy", analytics_enabled=False) as demo:

    # Tab for recording or uploading a speech sample to have it analyzed.
    # TODO - add callback functions
    with gr.Tab("Record speech"):
        # Flavor text
        gr.Markdown("# Language Buddy")
        gr.Markdown(f"This web application lets you study languages in a new way! You can record or upload your dialogue and the app will generate flashcards based on words it finds. ")

        # Language dropdown and audio widget
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
                    show_share_button=False,
                    type='filepath'
                )

                filename = gr.Textbox(visible=False)

        with gr.Row(equal_height=True):
            transcription = gr.Textbox(visible=False)
            feedback = gr.Textbox(visible=False)

        # Callback functions
        audio.change(
            fn=process_audio_file,
            inputs=[audio, selected_lang],
            outputs=[filename, transcription, feedback]
        )

    # Tab for viewing flashcards by language
    with gr.Tab("View flashcards"):
        gr.Markdown("# Flashcards Table")

        gr.Markdown("This page is a work in progress. You will eventually be able to add, update, and delete flashcards.")

        # Load the flashcard table from the DB
        # Currently supports Japanese - Spanish support to come soon
        flashcard_table_main, fc_table_df = load_fc_table()

        # Create a dropdown menu
        words = fc_table_df['word'].tolist()
        with gr.Row(equal_height=True):
            with gr.Column(scale=4):
                # Show the list of words
                word_selection = gr.Dropdown(words, interactive=True, label="Words")

            with gr.Column(scale=3):
                model_selection = gr.Dropdown(model_list, interactive=True, label="Model")

            # Agentic AI stuff
            with gr.Column(scale=1):
                translate_button = gr.Button("Translate this word to English")

        # Shows agent output
        output = gr.Textbox(visible=False)

        # Clicking the button calls the agent
        translate_button.click(
            fn=run_translation_agent,
            inputs=[word_selection, model_selection],
            outputs=[output]
        )
    
    # Sidebar
    with gr.Sidebar(position="left"):

        # Informational stuff
        # Reused from the streamlit version
        gr.Markdown("# Informational Links")
        # Github Link
        gr.Markdown("You can view the source code for Language Buddy by clicking the button below.")
        gr.Button("View Source Code", link="https://github.com/GoodGuyGregory/psu-language-buddy/tree/bugfixing")

        # LibreTranslate info
        gr.Markdown("This project requires the Python library for the free and open source LibreTranslate machine translation API.")
        gr.Markdown("Language Buddy is not officially associated with LibreTranslate or its products.")
        gr.Button("LibreTranslate official website", link="https://libretranslate.com/")
        gr.Button("pypi.org link", link="https://pypi.org/project/libretranslate/")

        # Info about not recording or uploading unwanted or confidential info
        gr.Markdown("Please do not record or upload unwanted or confidential information.")

# =============================================================================
# Launch the app
if __name__ == "__main__":
    demo.launch(
        inbrowser=True,             # Open a new browser window
        share=False,                # Don't share the app by default. To make the app public, change this line to True
        show_error=False,           # Set this to True for debugging purposes
        server_name="127.0.0.1",    # Default server name
        server_port=7860,           # Default server port
    )