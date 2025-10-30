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


# Imports
import streamlit as st
from pages.duckdb_fc import flashcard_table 

# ======================================================================

# Name of database
db_name_jp = "flashcards.duckdb" # For Japanese words
db_name_es = "flashcards_es.duckdb" # For Spanish words

# ======================================================================

db_lang = st.sidebar.selectbox("Select a language", [db_name_jp, db_name_es])

db_table = flashcard_table.DuckDB_Table(db_lang)

# ======================================================================
st.title("Flashcards Table")

st.write("Here are the flashcards you have created so far.")

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
table = db_table.read_DB()

# Show an editable table
# TODO - add delete button to delete selected rows
# TODO - add edit button to save changes to the DB
st.data_editor(table, num_rows="dynamic")