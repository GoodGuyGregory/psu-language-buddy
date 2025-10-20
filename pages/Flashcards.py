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

# Name of database
db_name_jp = "flashcards.duckdb" # For Japanese words
db_name_es = "flashcards_es.duckdb" # For Spanish words

# ======================================================================

db_lang = st.sidebar.selectbox("Select a language", [db_name_jp, db_name_es])
#db_lang = db_name_jp

db_table = flashcard_table.DuckDB_Table(db_lang)

# ======================================================================
st.title("Flashcards Table")

st.write("Here are the flashcards you have created so far.")

# Read the flashcards table and show it
table = db_table.read_DB()
st.table(table)