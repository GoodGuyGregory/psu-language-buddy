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
import duckdb # Import duckdb for database management
import os

# Name of database
db_name_jp = "flashcards.duckdb" # For Japanese words
db_name_es = "flashcards_es.duckdb" # For Spanish words

# =============================================================================
# Database functions (DuckDB)
# 6/8/2025 - placed them in a class

class DuckDB_Table():
    # Initialize the DB with the given DB name
    def __init__(self, db_name):
        self.db_name = db_name
        self.table_name = "flashcards"
        if db_name == db_name_jp:
           self.table_name = "flashcards"
        elif db_name == db_name_es:
            self.table_name = "flashcards_ES" 

    # Create the database of flashcards
    # This establishes a connection and creates flashcards.duckdb if the file is not already present
    def create_flashcards_DB(self):
        # Create the DB if it doesn't already exist
        create_flashcards_table = ""
        if not os.path.exists(self.db_name):
            con = duckdb.connect(database=self.db_name, read_only=False) # Connect to the DB
            create_seq = "CREATE SEQUENCE increment_id START 1;" # Auto incrementing id
            # Depending on the language, set up the schema
            if self.db_name == db_name_jp: # Japanese
                create_flashcards_table = f"""CREATE TABLE {self.table_name} (
                    id INTEGER DEFAULT nextval('increment_id'),
                    word VARCHAR,
                    meaning VARCHAR,
                    furigana VARCHAR,
                    romaji VARCHAR,
                    level INTEGER,
            
                )""" # Each row must have an id that can be incremented. Note that I did not specify id as the PRIMARY KEY
            elif self.db_name == db_name_es:
                create_flashcards_table = f"""CREATE TABLE {self.table_name} (
                    id INTEGER DEFAULT nextval('increment_id'),
                    word VARCHAR,
                    meaning VARCHAR,
                )""" # Each row must have an id that can be incremented. Note that I did not specify id as the PRIMARY KEY
            con.execute(create_seq) # Create the sequence
            con.execute(create_flashcards_table) # Create the table
            con.close() # Close the connection
    # If the DB already exists, do nothing
    

    # Insert a new flashcard into the database
    # 6/8/2025 - placed into class, added self param, merged parameters into a single list argument
    # 
    def create_DB_entry(self, word_params):

        # Extract parameters
        word = word_params['word']
        meaning = word_params['meaning']

        con = duckdb.connect(database=self.db_name, read_only=False)
        if self.db_name == db_name_jp:
            # Extract furigana, romaji, and level
            furigana = word_params['furigana']
            romaji = word_params['romaji']
            level = word_params['level']
            insert_flashcard = f"INSERT INTO {self.table_name} BY POSITION (word, meaning, furigana, romaji, level) VALUES ('{word}', '{meaning}', '{furigana}', '{romaji}', {level});"
        else:
            insert_flashcard = f"INSERT INTO {self.table_name} BY POSITION (word, meaning) VALUES ('{word}', '{meaning}');"
        con.execute(insert_flashcard)
        con.close()
    
    # Read the entire database and show it without the ID column
    # TODO
    def read_DB(self):
        if os.path.exists(self.db_name):
            read_table = ""
            con = duckdb.connect(database=self.db_name, read_only=False)
            if self.db_name == "flashcards.duckdb":
                read_table = f"SELECT word, meaning, furigana, romaji, level FROM {self.table_name}"
            else:
                read_table = f"SELECT word, meaning FROM {self.table_name}"
            res = con.execute(read_table)
            return res
    
    # Return the number of flashcards
    # https://duckdb.org/docs/stable/clients/python/conversion#pandas
    def count_flashcards(self):
        con = duckdb.connect(database=self.db_name, read_only=False)

        if self.db_name == db_name_jp:
            count_flashcards = f"SELECT count(*) FROM {self.table_name}"
        else:
            count_flashcards = f"SELECT count(*) FROM {self.table_name}"

        res = con.execute(count_flashcards).fetchdf() # Returns a duckdb connection object that can be turned into a table

        return res


    # Update a flashcard
    # TODO
    def update_DB_entry(self):
        return

    # Delete a flashcard by id
    # TODO
    def delete_DB_entry(self, id):
        flashcards = ""
        con = duckdb.connect(database=self.db_name, read_only=False)
        if self.db_name == db_name_jp:
            flashcards = "flashcards"
        else:
            flashcards = "flashcards_ES"
        delete_entry = f"DELETE FROM {flashcards} WHERE id == {id};"
        con.execute(delete_entry)

    # Delete the entire DB
    # This deletes the .duckdb file
    # WARNING - this cannot be undone!
    def delete_DB(self):
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
    

db_lang = st.sidebar.selectbox("Select a language", [db_name_jp, db_name_es])
#db_lang = db_name_jp

db_table = DuckDB_Table(db_lang)


table = db_table.read_DB()
st.table(table)