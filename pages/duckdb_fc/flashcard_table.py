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

import duckdb # Import duckdb for database management
import os
import pandas as pd

# Database functions (DuckDB)
# 6/8/2025 - placed them in a class
# 10/19/2025 - placed the class in a single file that will be used in all other Python files
# that need a DB

class DuckDB_Table():
    # Initialize the DB with the given DB name
    def __init__(self, db_name):
        self.db_name = db_name
        self.table_name = "flashcards"
        if db_name == "flashcards.duckdb":
           self.table_name = "flashcards"
        elif db_name == "flashcards_es.duckdb":
            self.table_name = "flashcards_ES" 

    # Create the database of flashcards
    # This establishes a connection and creates flashcards.duckdb if the file is not already present
    def create_flashcards_DB(self):
        # Create the DB if it doesn't already exist
        create_flashcards_table = ""
        #if not os.path.exists(self.db_name):
        con = duckdb.connect(database=self.db_name, read_only=False) # Connect to the DB
        create_seq = "CREATE SEQUENCE increment_id START 1;" # Auto incrementing id
        # Depending on the language, set up the schema
        if self.db_name == "flashcards.duckdb": # Japanese
            create_flashcards_table = f"""CREATE TABLE {self.table_name} (
                id INTEGER DEFAULT nextval('increment_id'),
                word VARCHAR,
                meaning VARCHAR,
                furigana VARCHAR,
                romaji VARCHAR,
                level INTEGER,
                delete BOOLEAN,
            )""" # Each row must have an id that can be incremented. Note that I did not specify id as the PRIMARY KEY
        elif self.db_name == "flashcards_es.duckdb":
            create_flashcards_table = f"""CREATE TABLE {self.table_name} (
                id INTEGER DEFAULT nextval('increment_id'),
                word VARCHAR,
                meaning VARCHAR,
                delete BOOLEAN,
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
        if self.db_name == "flashcards.duckdb":
            # Extract furigana, romaji, and level
            furigana = word_params['furigana']
            romaji = word_params['romaji']
            level = word_params['level']
            insert_flashcard = f"INSERT INTO {self.table_name} BY POSITION (word, meaning, furigana, romaji, level, delete) VALUES ('{word}', '{meaning}', '{furigana}', '{romaji}', {level}, false);"
        else:
            insert_flashcard = f"INSERT INTO {self.table_name} BY POSITION (word, meaning, delete) VALUES ('{word}', '{meaning}', false);"
        con.execute(insert_flashcard)
        con.close()
    
    # Read the entire database and show it without the ID column
    # TODO
    def read_DB(self) -> duckdb.DuckDBPyConnection:
        if os.path.exists(self.db_name):
            read_table = ""
            con = duckdb.connect(database=self.db_name, read_only=False)
            if self.db_name == "flashcards.duckdb":
                read_table = f"SELECT id, word, meaning, furigana, romaji, level, delete FROM {self.table_name}"
            else:
                read_table = f"SELECT id, word, meaning, delete FROM {self.table_name}"
            res = con.execute(read_table)
            return res
    
    # Return the number of flashcards
    # https://duckdb.org/docs/stable/clients/python/conversion#pandas
    def count_flashcards(self) -> pd.DataFrame:
        con = duckdb.connect(database=self.db_name, read_only=False)

        if self.db_name == "flashcards.duckdb":
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
        if self.db_name == "flashcards.duckdb":
            flashcards = "flashcards"
        else:
            flashcards = "flashcards_ES"
        delete_entry = f"DELETE FROM {flashcards} WHERE id == {id};"
        con.execute(delete_entry)

    # Update the DB when the data editor changes
    # This will delete the old DB and replace it with the new one
    # new_table is a Pandas dataframe
    def update_DB_editor(self, new_table):
        
        #print(new_table)
        # For handling Japanese words
        print("Dropping Table and sequence")
        self.drop_table()
        print("Recreating table and sequence")
        self.create_flashcards_DB()
        print("Inserting new data")
        if self.db_name == "flashcards.duckdb":
            for i in range(new_table.shape[0]):
                print(new_table.iloc[i].to_list())
                data = new_table.iloc[i].to_list()
                id = data[0]
                word = data[1]
                meaning = data[2]
                furigana = data[3]
                romaji = data[4]
                level = data[5]
                word_params = {"word": word, "meaning": meaning, "furigana": furigana, "romaji": romaji, "level": level}
                self.create_DB_entry(word_params)
        #con = duckdb.connect(database=self.db_name, read_only=False) # Connect to the DB

        #con.close()

    # Drop a specific table and the sequence
    def drop_table(self):
        con = duckdb.connect(database=self.db_name, read_only=False)
        if self.db_name == "flashcards.duckdb": # Japanese
            con.execute(f"DROP TABLE {self.table_name}") # Drop the table
            con.execute("DROP SEQUENCE increment_id") # Delete the sequence
        con.close()


    # Delete the entire DB
    # This deletes the .duckdb file
    # WARNING - this cannot be undone!
    def delete_DB(self):
        if os.path.exists(self.db_name):
            os.remove(self.db_name)