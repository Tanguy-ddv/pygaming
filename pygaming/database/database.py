"""
The Database is used to address queries to the database.
"""
import sqlite3 as sql
import os
from typing import Literal

from ..file import get_file
from ..config import Config

SERVER = 'server'
GAME = 'game'

class Database:
    """
    The Database instance is used to adress queries to the database.
    No need to have 2 databases on the same code as they will connect to the same db.
    The database automatically create a .sqlite file in the temporary folder /data/sql/db.sqlite,
    then execute every .sql file in the data/sql/ folder.
    At instance deletion, the .sqlite file is deleted if the debug mode is not selected.
    """

    def __init__(self, config: Config, runnable_type: Literal['server', 'game'] = GAME, debug: bool=False) -> None:
        """
        Initialize an instance of Database.
        
        Params:
        ---
        - config: the config of the runnable. It is used to collect the default language
        - runnable_type: 'server' or 'game', used to specifiy if it is the game's database or the server's database.
        - debug: when passed to true, the delation of the database is not done at the destruction of the instance.
        """
        self._debug = debug
        if runnable_type == SERVER:
            self._db_path = get_file('data','db-server.sqlite')
            self._table_path = get_file('data','sql-server/tables.sql')
            self._ig_queries_path = get_file('data', 'sql-server/ig_queries.sql')
            self._sql_folder = get_file('data', 'sql-server')
        if runnable_type == GAME:
            self._db_path = get_file('data', 'db-game.sqlite')
            self._table_path = get_file('data','sql-game/tables.sql')
            self._ig_queries_path = get_file('data', 'sql-game/ig_queries.sql')
            self._sql_folder = get_file('data', 'sql-game')

        # Remove the previous sqlite file if existing.
        if os.path.isfile(self._db_path):
            os.remove(self._db_path)

        # Create and connect to the sqlite file.
        self._conn = sql.connect(self._db_path)

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

        # Save the current language
        self.default_language = config.default_language

    def execute_select_query(self, query: str):
        """
        Execute a select query on the database.

        Params:
        ---
        - query: str, the query to execute. Must start by 'SELECT'

        Returns:
        ---
        - result: list[list[Any]]: The matrix of outputs
        - description: list[str]: The list of fields
        """
        if not (query.startswith("SELECT") or query.startswith("\nSELECT")):
            print("The query is wrong:\n", query, "\nShould start by 'SELECT'")
        try:
            cur = self._conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
            description = [descr[0] for descr in cur.description]
            cur.close()
            return result, description
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)
            return None, None

    def execute_insert_query(self, query: str):
        """
        Execute an insert query on the database.
        
        Params:
        ---
        - query: str, the query to execute. Need to start with 'INSERT INTO'
        """
        if not (query.startswith("INSERT INTO") or query.startswith("\nINSERT INTO")):
            print("The query is wrong:\n", query, "\nShould start by 'INSERT INTO'")
        try:
            # Execute the query on the database
            cur = self._conn.cursor()
            cur.execute(query)
            self._conn.commit()
            # Save the query on the ig_query file to execute it every time you launch the app.
            with open(self._ig_queries_path, 'a', encoding='utf-8') as f:
                f.write(";\n" + query)
            cur.close()
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)

    def execute_modify_query(self, query: str):
        """
        Execute a modifying query (UPDATE, DELETE, etc.) on the database.

        Params:
        ---
        - query: str, the query to execute. Needs to start with 'UPDATE', 'DELETE', 'ALTER TABLE', or similar.
        """
        valid_keywords = ["UPDATE", "DELETE", "ALTER TABLE", "DROP", "CREATE", "REPLACE",
            "\nUPDATE", "\nDELETE", "\nALTER TABLE", "\nDROP", "\nCREATE", "\nREPLACE"
        ]

        if not any(query.startswith(keyword) for keyword in valid_keywords):
            print("The query is wrong:\n", query, "\nShould start by one of:", ', '.join(valid_keywords))
            return

        try:
            # Execute the query on the database
            cur = self._conn.cursor()
            cur.execute(query)
            self._conn.commit()
            # Optionally log or save the query
            with open(self._ig_queries_path, 'a', encoding='utf-8') as f:
                f.write(";\n" + query)
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

    def __del__(self):
        """Destroy the Database object. Delete the database file"""
        self._conn.close()
        if os.path.isfile(self._db_path) and not self._debug:
            os.remove(self._db_path)

    def get_data_by_id(self, id_: int, table: str, return_id: bool = True):
        """Get all the data of one row based on the id and the table."""
        query = f"SELECT * FROM {table} WHERE {table}_id = {id_} LIMIT 1"
        result, description = self.execute_select_query(query)
        return {key : value for key,value in zip(description, result[0]) if (return_id or key != f"{table}_id")}

    def get_texts(self, language: str, phase_name:str):
        """Return all the texts of the game.
        If the text is not avaiable in the chosen language, get the text in the default language.
        """

        return self.execute_select_query(
            f"""SELECT position, text_value
                FROM localizations
                WHERE language_code = '{language}'
                AND ( phase_name = '{phase_name}' OR phase_name = 'all' )

                UNION

                SELECT position, text_value
                FROM localizations
                WHERE language_code = '{self.default_language}'
                AND ( phase_name = '{phase_name}' OR phase_name = 'all' )
                AND position NOT IN (
                    SELECT position
                    FROM localizations
                    WHERE language_code = '{language}'
                    AND ( phase_name = '{phase_name}' OR phase_name = 'all' )
            )"""
        )

    def get_texts(self, loc: str):
        """Return the texts that can be obtain for the same localization given any language."""
        return self.execute_select_query(
            f"""SELECT text_value 
            FROM localizations
            WHERE position = '{loc}'
            """
        )[0]

    def get_speeches(self, language: str, phase_name: str):
        """
        Return all the specches of the phase of the given language.
        If the speech is not available in the given language, get it in the default language
        """

        return self.execute_select_query(
            f"""SELECT position, sound_path
                FROM speeches
                WHERE language_code = '{language}'
                AND ( phase_name = '{phase_name}' OR phase_name = 'all' )

                UNION

                SELECT position, sound_path
                FROM speeches
                WHERE language_code = '{self.default_language}'
                AND ( phase_name = '{phase_name}' OR phase_name = 'all' )
                AND position NOT IN (
                    SELECT position
                    FROM speeches
                    WHERE language_code = '{language}'
                    AND ( phase_name = '{phase_name}' OR phase_name = 'all' )
            )"""
        )

    def get_sounds(self, phase_name: str):
        """
        Return all the sounds of the phase.
        """

        sounds = self.execute_select_query(
            f"""SELECT name, sound_path, category
                FROM sounds
                WHERE ( phase_name = '{phase_name}' OR phase_name = 'all' )
            """
        )[0]
        return {sound_name : (sound_path, category) for sound_name, sound_path, category in sounds}

    def get_fonts(self, phase_name: str):
        """
        Return all the fonts of the phase.
        """

        fonts = self.execute_select_query(
            f"""SELECT name, font_path, size, italic, bold, underline, strikethrough
                FROM fonts
                WHERE ( phase_name = '{phase_name}' OR phase_name = 'all' )
            """
        )[0]
        return {font_name : (font_path, size, italic, bold, underline, strikethrough ) for font_name, font_path, size, italic, bold, underline, strikethrough in fonts}
