"""
The Database is used to address queries to the database.
"""
import sqlite3 as sql
import os
from ..file.file import get_file
from ..config import Config
from typing import Literal

SERVER = 'server'
GAME = 'game'

class Database:
    """
    The Database instance is used to adress queries to the database.
    No need to have 2 databases on the same code as they will connect to the same db.
    The database automatically create a .sqlite file in the temporary folder /data/sql/db.sqlite,
    then execute every .sql file in the data/sql/ folder.
    At instance deletion, the .sqlite file is deleted if the debug mode is not selected ()
    
    """

    def __init__(self, config: Config, runnable_type: Literal['server', 'game'] = GAME, debug: bool=False) -> None:
        """
        Initialize an instance of Database.
        
        args:
        debug: when passed to true, the delation of the database is not done at the destruction of the instance.
        """
        self._debug = debug
        if runnable_type == SERVER:
            self._db_path = get_file('data','db-server.sqlite')
            self._table_path = get_file('data','sql-server/tables.sql')
            self._ig_queries_path = get_file('data', 'sql-server/ig_queries.sql', permanent=False)
            self._sql_folder = get_file('data', 'sql-server')
        if runnable_type == GAME:
            self._db_path = get_file('data', 'db-game.sqlite')
            self._table_path = get_file('data','sql-game/tables.sql')
            self._ig_queries_path = get_file('data', 'sql-game/ig_queries.sql', permanent=False)
            self._sql_folder = get_file('data', 'sql-game')

        # Remove the previous sqlite file if existing.
        if os.path.isfile(self._db_path):
            os.remove(self._db_path)

        # Create and connect to the sqlite file.
        self._conn = sql.connect(self._db_path)

        # Initialize the sqlite file with the tables.
        self._execute_sql_script(self._table_path)

        for root, _, files in os.walk(self._sql_folder):
            for file in files:
                complete_path = os.path.join(root, file).replace('\\', '/')
                if complete_path.endswith('.sql') and complete_path != self._table_path and complete_path != self._ig_queries_path:
                    if self._debug:
                        print(complete_path)
                    self._execute_sql_script(complete_path)
        
        # Execute the queries previously saved.
        self._execute_sql_script(self._ig_queries_path)
        self.default_language = config.default_language

    def _execute_select_query(self, query: str):
        """Execute a select query on the database."""
        if not query.startswith("SELECT"):
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

    def _execute_insert_query(self, query: str):
        """Execute an insert query on the database."""
        if not query.startswith("INSERT INTO"):
            print("The query is wrong:\n", query, "\nShould start by 'INSERT INTO'")
            return None
        try:
            # Execute the query on the Database
            cur = self._conn.cursor()
            cur.execute(query)
            self._conn.commit()
            # Save the query on the ig_query file to execute it every time you launch the app.
            with open(self._ig_queries_path, 'a', encoding='utf-8') as f:
                f.write(";\n" + query)
            cur.close()
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)

    def _execute_sql_script(self, script_path: str):
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
        result, description = self._execute_select_query(query)
        return {key : value for key,value in zip(description, result[0]) if (key != f"{table}_id" or return_id)}
    
    def get_collection_joined_by_id(self, id_, table: str, join_table: str, return_id: bool = True) -> list:
        """Get all the row of a the table 'table' having has foreign key for the table 'join_table' the id id_"""
        query = f"SELECT * FROM {table} WHERE {join_table}_id = {id_}"
        result, description = self._execute_select_query(query)
        return [{key : value for key,value in zip(description, res) if (key != f"{table}_id" or return_id)} for res in result]

    def get_texts(self, language: str):
        """Return all the texts of the game.
        If the text is not avaiable in the chosen language, get the text in the default language.
        """

        return self._execute_select_query(
            f"""SELECT position, text_value
                FROM localizations
                WHERE language_code = '{language}'

                UNION

                SELECT position, text_value
                FROM localizations
                WHERE language_code = '{self.default_language}'
                AND position NOT IN (
                    SELECT position
                    FROM localizations
                    WHERE language_code = '{language}'
            )"""
        )
    
    def get_speeches(self, language: str):
        """
        Return all the specches of the game of the given language.
        If the speech is not available in the given language, get it in the default language
        """

        return self._execute_select_query(
            f"""SELECT position, sound_path
                FROM speeches
                WHERE language_code = '{language}'

                UNION

                SELECT position, sound_path
                FROM speeches
                WHERE language_code = '{self.default_language}'
                AND position NOT IN (
                    SELECT position
                    FROM speeches
                    WHERE language_code = '{language}'
            )"""
        )