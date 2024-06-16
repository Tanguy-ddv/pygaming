"""
The Database is used to address queries to the database.
"""
import sqlite3 as sql
import os

class Database:
    """The Database is used to adress queries to the database."""

    def __init__(self, db_path: str, table_sql_path: str, script_path_folder, in_game_script_path: str, debug: bool=False) -> None:
        """
        Initialize an instance of Databas.
        
        args:
        db_path: The path to the database.
        table_sql_path: the path to the sql file that creates tables.
        script_path_folder: the folder containging all the sql files to be executed.
        in_game_script_path: The path to the sql file that stores every insert queries executed during the games.
        debug: when passed to true, the delation of the database is not done at the destruction of the instance.
        """
        self._db_path = db_path
        self._debug = debug
        self._in_game_script_path = in_game_script_path
        self._create_database(table_sql_path, script_path_folder, in_game_script_path)

    def _execute_select_query(self, query: str):
        """Execute a select query on the database."""
        if not query.startswith("SELECT"):
            print("The query is wrong:\n", query, "\nShould start by 'SELECT'")
        if not os.path.isfile(self._db_path):
            print("The database has not been created yet.")
        try:
            conn = sql.connect(self._db_path)
            cur = conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
            description = [description[0] for description in cur.description]
            cur.close()
            conn.close()
            return result, description
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)

    def _execute_insert_query(self, query: str):
        """Execute an insert query on the database."""
        if not query.startswith("INSERT INTO"):
            print("The query is wrong:\n", query, "\nShould start by 'INSERT INTO'")
            return None
        if not os.path.isfile(self._db_path):
            print("The database has not been created yet.")
            return None
        try:
            conn = sql.connect(self._db_path)
            cur = conn.cursor()
            cur.execute(query)
            with open(self._in_game_script_path, 'a', encoding='utf-8') as f:
                f.write(";\n" + query)
            conn.commit()
            cur.close()
            conn.close()
        except sql.Error as error:
            print("An error occured while querying the database with:\n",query,"\n",error)

    def _execute_sql_script(self, script_path: str):
        """Execute a script query on the database."""
        try:
            conn = sql.connect(self._db_path)
            cur = conn.cursor()
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            if script:
                cur.executescript(script)
                conn.commit()
                cur.close()
                conn.close()
                
        except sql.Error as error:
            print("An error occured while querying the database with the script located at\n",script_path,"\n",error)            

    def _create_database(self, table_sql_path: str, script_path_folder: str, in_game_script_path: str):
        """
        Create the database and execute the scripts in it.

        table_sql_path: the path to the sql file that creates tables.
        script_path_folder: the path to the folder containing all the scripts.
        """
        if os.path.isfile(self._db_path):
            os.remove(self._db_path)

        conn = sql.connect(self._db_path)
        conn.close()

        self._execute_sql_script(table_sql_path)

        for root, _, files in os.walk(script_path_folder):
            for file in files:
                complete_path = os.path.join(root, file)
                if complete_path.endswith('.sql') and complete_path.replace('\\','/') != table_sql_path and complete_path.replace('\\','/') != in_game_script_path:
                    if self._debug:
                        print(complete_path)
                    self._execute_sql_script(complete_path)
        
        self._execute_sql_script(in_game_script_path)


    def __del__(self):
        """Destroy the DatabaseManager. Delete the database"""
        if os.path.isfile(self._db_path) and not self._debug:
            os.remove(self._db_path)

    def get_data_by_id(self, id_: int, table: str, return_id: bool = True):
        """Get all the data of one row based on the id and the table."""
        query = f"SELECT * FROM {table} WHERE {table}_id = {id_} LIMIT 1"
        result, description = self._execute_select_query(query)
        return {key : value for key,value in zip(description, result[0]) if (key != f"{table}_id" or return_id)}
    
    def get_collection_joined_by_id(self, id_, table: str, join_table: str, return_id: bool = True) -> list:
        """Get all the row of a the table 'table' having has foreign key for the table 'join_table' the id_"""
        query = f"SELECT * FROM {table} WHERE {join_table}_id = {id_}"
        result, description = self._execute_select_query(query)
        return [{key : value for key,value in zip(description, res) if (key != f"{table}_id" or return_id)} for res in result]
    