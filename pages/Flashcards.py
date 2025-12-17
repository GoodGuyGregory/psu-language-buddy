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

# This is a separate app page for showing the flashcards table and manipulating it in various ways
# 10/10/2025
# Some ideas are from https://discuss.streamlit.io/t/select-and-delete-row-in-st-data-editor-using-native-checkbox/92929
#
# Requires Anthropic API key and OpenAI API key to be defined in the user's environment variables.

# Imports
import streamlit as st
from pages.duckdb_fc import flashcard_table 
from agents import Agent, Runner    # Agentic AI stuff
from agents.extensions.models.litellm_model import LitellmModel # For using other models
import os
# ======================================================================

# Name of database
db_name_jp = "flashcards.duckdb" # For Japanese words
db_name_es = "flashcards_es.duckdb" # For Spanish words

# ======================================================================

db_lang = st.sidebar.selectbox("Select a language", [db_name_jp, db_name_es])

db_table = flashcard_table.DuckDB_Table(db_lang)

# ======================================================================


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
    model=LitellmModel(model="anthropic/claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY"))
)

# Run the agent above to translate a word using an agent
# Please keep in mind that the user needs to double check translations
def run_translation_agent(word: str, model: str):
    selected_agent = None
    # Execute the agent
    if model == "gpt-4.1": # If the user selected gpt-4.1, run this specific agent
        selected_agent = translation_agent_openai
    elif model == "gpt-4o":
        selected_agent = translation_agent_openai_4o
    elif model == "claude-sonnet-4.5":
        selected_agent = translation_agent_claude
    else: # Unsupported model
        st.error("ERROR: This model is not supported. Please try a different model.")
        return 
    
    # Supported model - print the final output
    # This uses run_sync because the async keyword does not work with my Streamlit app
    result = Runner.run_sync(
        selected_agent, 
        f"What is the English meaning of {word}?"
    )
    print(result.final_output)
    st.write("Here is the translation. Please double-check the result with a native speaker.")
    st.write(result.final_output)
    return


# Models to select
model_list = ['gpt-4.1', 'gpt-4o', "claude-sonnet-4.5", 'test model']


# ======================================================================
# Update the whole DB using the changes specified by the user
def update_DB(duckdb_table, new_table):
    duckdb_table.update_DB_editor(new_table)
# ======================================================================

st.title("Flashcards Table")



# Informational stuff
st.sidebar.info("Informational Links")
# Github Link
st.sidebar.write("You can view the source code for Language Buddy by clicking the button below.")
st.sidebar.link_button("View Source Code", "https://github.com/GoodGuyGregory/psu-language-buddy/tree/bugfixing")

# LibreTranslate info
st.sidebar.write("This project requires the Python library for the free and open source LibreTranslate machine translation API.")
st.sidebar.write("Language Buddy is not officially associated with LibreTranslate or its products.")
st.sidebar.link_button("LibreTranslate official website", "https://libretranslate.com/")
st.sidebar.link_button("pypi.org link", "https://pypi.org/project/libretranslate/")

# Read the flashcards table and show it
try:
    table = db_table.read_DB()
except:
    st.info(f"Table {db_table.table_name} does not exist for {db_table.db_name}")
    #table = db_table.create_flashcards_DB()
else:

    # Only show certain buttons when the database is populated

    # Show an editable table
    # TODO - add delete button to delete selected rows
    df = st.data_editor(
        table, 
        num_rows="dynamic",
        column_config={
                "id": st.column_config.NumberColumn(disabled=False),
                "Delete": st.column_config.CheckboxColumn("Delete")
            }
        )
    
    if df.empty:
        st.write("No flashcards here!")
    else:
        st.write("Here are the flashcards you have created so far.")

    if not df.empty:
        # Update button
        update_button = st.button("Update DB")

        # If the button is pressed, update the DB with the changes shown in the data editor
        if update_button:
            # Update DB
            # Do not include rows that have the Delete checkbox checked.
            modified_df = df[df["delete"] == False]
            update_DB(duckdb_table=db_table, new_table=modified_df)


    # Agentic AI stuff
    if not df.empty:
        word = st.selectbox("Select a word", df['word'])
        agentic_model = st.selectbox("Select a model", model_list)
        agentic_translate_button = st.button("Translate word")

        if agentic_translate_button:
            run_translation_agent(word, agentic_model)