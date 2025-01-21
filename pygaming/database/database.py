"""
The Database is used to address queries to the database.
"""
import sqlite3 as sql
import os
from typing import Literal

from ..file import get_file
from ..state import State
from ..config import Config

SERVER = 'server'
GAME = 'game'

class Database:
    """
    The Database instance is used to adress queries to the database.
    No need to have 2 databases on the same code as they will connect to the same db.
    The database automatically create a .sqlite file in the folder /data/sql/db.sqlite,
    then execute every .sql file in the data/sql/ folder.
    At instance deletion, the .sqlite file is deleted if the debug mode is not selected.
    """

    def __init__(self, config: Config, state: State, runnable_type: Literal['server', 'game'] = GAME, debug: bool=False) -> None:
        """
        Initialize an instance of Database.
        
        Params:
        ---
        - config: the config of the runnable. It is used to collect the default language
        - runnable_type: 'server' or 'game', used to specifiy if it is the game's database or the server's database.
        - debug: when passed to true, the delation of the database is not done at the destruction of the instance.
        """
        # Save the config
        self._config = config
        self._debug = debug

        # Save some paths
        self._db_path = get_file('data',f'db-{runnable_type}.sqlite')
        self._table_path = get_file('data',f'sql-{runnable_type}/tables.sql')
        self._ig_queries_path = get_file('data', f'sql-{runnable_type}/ig_queries.sql')
        self._sql_folder = get_file('data', f'sql-{runnable_type}')

        # Get current state
        self.__entry = f"ig_queries_{runnable_type}_threshold_size_kb"
        self._state = state
        self._threshold_size = self._state.get_state()[self.__entry]

        # If the current state is 0, then set it to the first value of the increment
        # as it means that the state have not been udpated once.
        if self._threshold_size == 0:
            self._threshold_size = self._config.get(self.__entry, 1000)

        # Remove the previous sqlite file if existing.
        if os.path.isfile(self._db_path):
            os.remove(self._db_path)

        # Create and connect to the sqlite database.
        self._conn = sql.connect(self._db_path if (debug or not config.get(f"in_memory_{runnable_type}_db", False)) else ":memory:")

        # Initialize the sqlite file with the tables.
        self.execute_sql_script(self._table_path)

        for root, _, files in os.walk(self._sql_folder):
            for file in files:
                complete_path = os.path.join(root, file).replace('\\', '/')
                if complete_path.endswith('.sql') and complete_path != self._table_path and complete_path != self._ig_queries_path:
                    if self._debug:
                        print(complete_path)
                    self.execute_sql_script(complete_path)

        # Execute the queries previously saved.
        self.execute_sql_script(self._ig_queries_path)

        self._ig_queries_file = open(self._ig_queries_path, 'a', encoding='utf-8')

    def reduce_ig_queries_size(self):
        """
        Reduce the size of the ig_queries file script.
        This file contains all the queries executed since the beginning of the game.
        its size can grow fast. With this function, all tables from the config argument
        "permanent_tables" are dumped into "INSERT INTO" queries and the queries overwrite
        the current version of the ig_queries file.
        """
        dumps = self._conn.iterdump()
        permanent_tables = self._config.get("permanent_tables")
        if permanent_tables:
            dumps_to_keep = (
                dump for dump in dumps
                if any(dump.startswith(f'INSERT INTO "{table}"') for table in permanent_tables)
            )
            with open(self._ig_queries_path, 'w', encoding='utf-8') as f:
                f.writelines(f"{dump}\n" for dump in dumps_to_keep)

    def execute_select_query(self, query: str, params: tuple = ()):
        """
        Execute a select query on the database.

        Params:
        ---
        - query: str, the query to execute
        - params: tuple, the params of the query

        Returns:
        ---
        - result: list[list[Any]]: The matrix of outputs
        - description: list[str]: The list of fields
        """
        try:
            cur = self._conn.cursor()
            cur.execute(query, params)
            result = cur.fetchall()
            description = [descr[0] for descr in cur.description]
            cur.close()
            return result, description
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)
            return [], []

    def execute_insert_query(self, query: str, params: tuple = ()):
        """
        Execute an insert query on the database.
        
        Params:
        ---
        - query: str, the query to execute. Need to start with 'INSERT INTO'
        - params: tuple, the params of the query
        """
        try:
            # Execute the query on the database
            cur = self._conn.cursor()
            cur.execute(query, params)
            self._conn.commit()
            # Save the query on the file
            self._ig_queries_file.write(query + ";\n")
            cur.close()
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)

    def execute_modify_query(self, query: str, params: tuple = ()):
        """
        Execute a modifying query (UPDATE, DELETE, etc.) on the database.

        Params:
        ---
        - query: str, the query to execute. Needs to start with 'UPDATE', 'DELETE', 'ALTER TABLE', or similar.
        - params: tuple, the params of the query
        """
        try:
            # Execute the query on the database
            cur = self._conn.cursor()
            cur.execute(query, params)
            self._conn.commit()
            # Save the query on the file
            self._ig_queries_file.write(query + ";\n")
            cur.close()
        except sql.Error as error:
            print("An error occurred while querying the database with:\n", query, "\n", error)

    def execute_sql_script(self, script_path: str):
        """Execute a script query on the database."""
        try:
            cur = self._conn.cursor()
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            if script:
                cur.executescript(script)
                self._conn.commit()
                cur.close()

        except sql.Error as error:
            print("An error occured while querying the database with the script located at\n",script_path,"\n",error)

    def close(self):
        """Destroy the Database object. Delete the database file"""
        self._ig_queries_file.close()

        # Reduce the ig_queries file
        ig_queries_size = os.path.getsize(self._ig_queries_path) / 1024
        if ig_queries_size > self._threshold_size:
            self.reduce_ig_queries_size()
            new_size = os.path.getsize(self._ig_queries_path) // 1024
            # Increase the threshold.
            self._state.set_state(self.__entry, new_size + self._config.get(self.__entry, 1000))

        # Close the connection and delete the database
        self._conn.close()
        if os.path.isfile(self._db_path) and not self._debug:
            os.remove(self._db_path)

    def get_data_by_id(self, id_: int, table: str, return_id: bool = True):
        """Get all the data of one row based on the id and the table."""
        query = f"SELECT * FROM {table} WHERE {table}_id = {id_} LIMIT 1"
        result, description = self.execute_select_query(query)
        return {key : value for key,value in zip(description, result[0]) if (return_id or key != f"{table}_id")}

    def get_language_texts(self, language: str, phase_name:str):
        """Return all the texts of the game.
        If the text is not avaiable in the chosen language, get the text in the default language.
        """

        return self.execute_select_query(
            """
            WITH this_language AS (
                SELECT position, text_value
                FROM localizations
                WHERE language_code = ?
                AND (
                    (phase_name_or_tag IN (SELECT tag FROM tags WHERE phase_name = ?))
                OR 
                    (phase_name_or_tag = ?)
                )
            )

            SELECT * from this_language

            UNION
            
            SELECT position, text_value
            FROM localizations
            WHERE language_code = ?
            AND (
                    (phase_name_or_tag IN (SELECT tag FROM tags WHERE phase_name = ?))
                OR 
                    (phase_name_or_tag = ?)
            )
            AND NOT EXISTS (
                SELECT 1 
                FROM this_language tl 
                WHERE tl.position = localizations.position
            )
            """,
            params = (
                language, phase_name, phase_name,  # For this_language CTE
                self._config.default_language, phase_name, phase_name  # For fallback query
            )
        )[0]

    def get_loc_texts(self, loc: str):
        """Return the texts that can be obtain for the same localization given any language."""
        return self.execute_select_query(
            """SELECT text_value 
            FROM localizations
            WHERE position = ?
            """,
            params=(loc,)
        )[0]

    def get_speeches(self, language: str, phase_name: str):
        """
        Return all the specches of the phase of the given language.
        If the speech is not available in the given language, get it in the default language
        """

        return self.execute_select_query(
            """
            WITH this_language AS (
                SELECT position, sound_path
                FROM speeches
                WHERE language_code = ?
                AND (
                    (phase_name_or_tag IN (SELECT tag FROM tags WHERE phase_name = ?))
                OR 
                    (phase_name_or_tag = ?)
                )
            )

            SELECT * from this_language

            UNION
            
            SELECT position, sound_path
            FROM speeches
            WHERE language_code = ?
            AND (
                    (phase_name_or_tag IN (SELECT tag FROM tags WHERE phase_name = ?))
                OR 
                    (phase_name_or_tag = ?)
            )
            AND NOT EXISTS (
                SELECT 1 
                FROM this_language tl 
                WHERE tl.position = speeches.position
            )
            """,
            params = (
                language, phase_name, phase_name,  # For this_language CTE
                self._config.default_language, phase_name, phase_name  # For fallback query
            )
        )[0]

    def get_sounds(self, phase_name: str):
        """
        Return all the sounds of the phase.
        """

        sounds = self.execute_select_query(
            """SELECT name, sound_path, category
                FROM sounds
                WHERE 
                    (phase_name_or_tag IN (SELECT tag FROM tags WHERE phase_name = ?))
                OR 
                    (phase_name_or_tag = ?)
            """,
            params=(phase_name, phase_name)
        )[0]
        return {sound_name : (sound_path, category) for sound_name, sound_path, category in sounds}

    def get_fonts(self, phase_name: str):
        """
        Return all the fonts of the phase.
        """

        fonts = self.execute_select_query(
            """SELECT name, font_path, size, italic, bold, underline, strikethrough
                FROM fonts
                WHERE 
                    (phase_name_or_tag IN (SELECT tag FROM tags WHERE phase_name = ?))
                OR 
                    (phase_name_or_tag = ?)
            """,
            params=(phase_name, phase_name)
        )[0]
        return {font_name : (font_path, size, italic, bold, underline, strikethrough) for font_name, font_path, size, italic, bold, underline, strikethrough in fonts}
