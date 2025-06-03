import psycopg2
import os
from psycopg2 import sql
from psycopg2.extras import execute_values
import csv

user = os.environ.get('PGPUSER', 'postgres')
password = os.environ.get('PGPASSWORD', '123')
host = os.environ.get('HOST', 'database')
dbname = os.environ.get('POSTGRES_DB', 'todo')

def db_connection():
    db = "dbname='todo' user=" + user + " host=" + host + " password=" + password # Corrected password concatenation
    conn = psycopg2.connect(db)
    return conn

def to_int_or_none(value_str):
    if value_str is None or value_str.strip() == '':
        return None
    try:
        return int(value_str)
    except ValueError:
        print(f"Warning: Could not convert '{value_str}' to int, using None instead.")
        return None

def to_float_or_none(value_str):
    if value_str is None or value_str.strip() == '':
        return None
    try:
        return float(value_str.replace(',', '.'))
    except ValueError:
        print(f"Warning: Could not convert '{value_str}' to float, using None instead.")
        return None

def insert_data(conn, table_name, columns, data_tuples, conflict_column=None):
    if not data_tuples:
        print(f"No data provided for insertion into {table_name}.")
        return
    with conn.cursor() as cur:
        cols_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
        table_sql = sql.Identifier(table_name)
        
        insert_query_base = "INSERT INTO {} ({}) VALUES %s".format(table_sql.string, cols_sql.as_string(cur)) # Use .string and .as_string for safety with sql.SQL format
        
        if conflict_column:
            conflict_sql = sql.Identifier(conflict_column)
            # Correctly format the SQL string with placeholders for sql.SQL objects
            insert_query_template = "INSERT INTO {} ({}) VALUES %s ON CONFLICT ({}) DO NOTHING"
            insert_query = sql.SQL(insert_query_template).format(table_sql, cols_sql, conflict_sql)
        else:
            insert_query_template = "INSERT INTO {} ({}) VALUES %s"
            insert_query = sql.SQL(insert_query_template).format(table_sql, cols_sql)

        try:
            execute_values(cur, insert_query, data_tuples)
            conn.commit()
            print(f"Successfully inserted/updated data into table {table_name}. {cur.rowcount} rows affected.")
        except Exception as e:
            print(f"Error inserting data into table {table_name}: {e}")
            conn.rollback()
            raise

def create_tables_if_not_exist(conn):
    table_definitions = [
        """
        CREATE TABLE IF NOT EXISTS courses (
            id VARCHAR(10) PRIMARY KEY,
            language VARCHAR(100),
            degree VARCHAR(10),
            examtype VARCHAR(100),
            title VARCHAR(1000),
            etcs VARCHAR(4),
            duration INTEGER,
            department VARCHAR(100)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS statistics (
            id VARCHAR(10) PRIMARY KEY,
            mean REAL,
            totalstudents INTEGER,
            pass INTEGER,
            fail INTEGER,
            passrate REAL,
            median REAL,
            absent INTEGER,
            "_minus3" INTEGER,
            "_00" INTEGER,
            "_02" INTEGER,
            "_4" INTEGER,
            "_7" INTEGER,
            "_10" INTEGER,
            "_12" INTEGER,
            CONSTRAINT fk_course_statistics
                FOREIGN KEY(id)
                REFERENCES courses(id)
                ON DELETE CASCADE
        );
        """,
        """
        DROP TABLE IF EXISTS admissions; 
        CREATE TABLE admissions(
            program_id VARCHAR(100) PRIMARY KEY, -- Set program_ID as PRIMARY KEY
            quota FLOAT,
            standbyquota VARCHAR(50),        -- Increased size for "Alle optaget, ledige pladser"
            admitted INT,
            perdistribution1 INT,            -- Corrected typo
            perdistribution2 INT,
            applications1 INT,
            applications2 INT, 
            averageage FLOAT,
            percentageofmen INT,
            percentageofwomen INT
        );
        """
    ]
    try:
        with conn.cursor() as cur:
            for table_def in table_definitions:
                cur.execute(table_def)
            conn.commit()
        print("Tables created or already existed according to the specified schema.")
    except psycopg2.Error as e:
        print(f"Error when creating tables: {e}")
        conn.rollback()
        raise

def import_to_postgresql():
    conn = None
    try:
        conn = db_connection()
        create_tables_if_not_exist(conn)

        # --- Import Courses ---
        courses_to_insert = []
        columns_for_courses = ['id', 'language', 'degree', 'examtype', 'title', 'etcs', 'duration', 'department']
        courses_csv_file_path = 'Database_files/courses.csv'

        try:
            with open(courses_csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',')
                print(f"Reading data from {courses_csv_file_path}...")
                for row_number, row_values in enumerate(reader, 1):
                    if not any(field.strip() for field in row_values):
                        print(f"Warning: Courses CSV Row {row_number} is empty. Skipping.")
                        continue
                    if len(row_values) != len(columns_for_courses):
                        print(f"Warning: Courses CSV Row {row_number} has {len(row_values)} values, expected {len(columns_for_courses)}. Skipping row: {row_values}")
                        continue
                    try:
                        processed_row = (
                            row_values[0].strip(), row_values[1].strip(), row_values[2].strip(),
                            row_values[3].strip(), row_values[4].strip(), row_values[5].strip(),
                            to_int_or_none(row_values[6]), row_values[7].strip()
                        )
                        courses_to_insert.append(processed_row)
                    except IndexError:
                        print(f"Warning: Courses CSV Row {row_number} does not have enough columns. Skipping row: {row_values}")
                    except Exception as e_row:
                        print(f"Warning: Error processing Courses CSV row {row_number}: {row_values}. Error: {e_row}. Skipping row.")
            if courses_to_insert:
                print(f"Attempting to insert {len(courses_to_insert)} records into 'courses' table.")
                insert_data(conn, 'courses', columns_for_courses, courses_to_insert, conflict_column='id')
            else:
                print(f"No valid data found or processed from {courses_csv_file_path} to insert into 'courses' table.")
        except FileNotFoundError:
            print(f"Error: The file {courses_csv_file_path} was not found.")
        except Exception as e_file:
            print(f"Error reading or processing file {courses_csv_file_path}: {e_file}")

        # --- Import Statistics ---
        statistics_to_insert = []
        columns_for_stats = [
            'id', 'mean', 'totalstudents', 'pass', 'fail', 'passrate', 'median', 'absent',
            '_minus3', '_00', '_02', '_4', '_7', '_10', '_12'
        ]
        stats_csv_file_path = 'Database_files/statistics.csv'
        try:
            with open(stats_csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',')
                print(f"Reading data from {stats_csv_file_path}...")
                for row_number, row_values in enumerate(reader, 1):
                    if not any(field.strip() for field in row_values):
                        print(f"Warning: Statistics CSV Row {row_number} is empty. Skipping.")
                        continue
                    if len(row_values) != len(columns_for_stats):
                        print(f"Warning: Statistics CSV Row {row_number} has {len(row_values)} values, expected {len(columns_for_stats)}. Skipping row: {row_values}")
                        continue
                    try:
                        processed_row = (
                            row_values[0].strip(), to_float_or_none(row_values[1]), to_int_or_none(row_values[2]),
                            to_int_or_none(row_values[3]), to_int_or_none(row_values[4]), to_float_or_none(row_values[5]),
                            to_float_or_none(row_values[6]), to_int_or_none(row_values[7]), to_int_or_none(row_values[8]),
                            to_int_or_none(row_values[9]), to_int_or_none(row_values[10]), to_int_or_none(row_values[11]),
                            to_int_or_none(row_values[12]), to_int_or_none(row_values[13]), to_int_or_none(row_values[14])
                        )
                        statistics_to_insert.append(processed_row)
                    except IndexError:
                        print(f"Warning: Statistics CSV Row {row_number} does not have enough columns. Skipping row: {row_values}")
                    except Exception as e_row:
                        print(f"Warning: Error processing Statistics CSV row {row_number}: {row_values}. Error: {e_row}. Skipping row.")
            if statistics_to_insert:
                print(f"Attempting to insert {len(statistics_to_insert)} records into 'statistics' table.")
                insert_data(conn, 'statistics', columns_for_stats, statistics_to_insert, conflict_column='id')
            else:
                print(f"No valid data found or processed from {stats_csv_file_path} to insert into 'statistics' table.")
        except FileNotFoundError:
            print(f"Error: The file {stats_csv_file_path} was not found.")
        except Exception as e_file:
            print(f"Error reading or processing file {stats_csv_file_path}: {e_file}")

        # --- Import Admissions ---
        admissions_to_insert = []
        columns_for_admissions = [
            'program_id', 'quota', 'standbyquota', 'admitted', 'perdistribution1', 
            'perdistribution2', 'applications1', 'applications2', 'averageage', 
            'percentageofmen', 'percentageofwomen'
        ]
        admissions_csv_file_path = 'Database_files/admission.csv' # Assuming this is the name of your new CSV file

        try:
            with open(admissions_csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',')
                header = next(reader) # Skip header row
                if [col.strip() for col in header] != columns_for_admissions: # Basic header check
                    print(f"Warning: CSV header {header} does not match expected columns {columns_for_admissions}")
                    # Decide if you want to stop or proceed with caution
                
                print(f"Reading data from {admissions_csv_file_path}...")
                for row_number, row_values in enumerate(reader, 1): # Start row_number from 1 for data rows
                    if not any(field.strip() for field in row_values):
                        print(f"Warning: Admissions CSV Row {row_number} is empty. Skipping.")
                        continue
                    if len(row_values) != len(columns_for_admissions):
                        print(f"Warning: Admissions CSV Row {row_number} has {len(row_values)} values, expected {len(columns_for_admissions)}. Skipping row: {row_values}")
                        continue
                    
                    try:
                        processed_row = (
                            row_values[0].strip(),                       # program_ID
                            to_float_or_none(row_values[1]),             # quota
                            row_values[2].strip(),                       # standbyquota
                            to_int_or_none(row_values[3]),               # admitted
                            to_int_or_none(row_values[4]),               # perdistribution1
                            to_int_or_none(row_values[5]),               # perdistribution2
                            to_int_or_none(row_values[6]),               # applications1
                            to_int_or_none(row_values[7]),               # applications2
                            to_float_or_none(row_values[8]),             # averageage
                            to_int_or_none(row_values[9]),               # percentageofmen
                            to_int_or_none(row_values[10])               # percentageofwomen
                        )
                        admissions_to_insert.append(processed_row)
                    except IndexError:
                        print(f"Warning: Admissions CSV Row {row_number} does not have enough columns. Skipping row: {row_values}")
                    except Exception as e_row:
                        print(f"Warning: Error processing Admissions CSV row {row_number}: {row_values}. Error: {e_row}. Skipping row.")
            
            if admissions_to_insert:
                print(f"Attempting to insert {len(admissions_to_insert)} records into 'admissions' table.")
                insert_data(conn, 'admissions', columns_for_admissions, admissions_to_insert, conflict_column='program_id')
            else:
                print(f"No valid data found or processed from {admissions_csv_file_path} to insert into 'admissions' table.")

        except FileNotFoundError:
            print(f"Error: The file {admissions_csv_file_path} was not found.")
        except Exception as e_file:
            print(f"Error reading or processing file {admissions_csv_file_path}: {e_file}")
    
    except psycopg2.Error as e_db:
        print(f"PostgreSQL database error during import process: {e_db}")
    except Exception as e_general:
        print(f"A general error occurred during the import process: {e_general}")
    finally:
        if conn:
            conn.close()
            print("Closed PostgreSQL connection.")


def to_float_or_none(value_str):
    if value_str is None or value_str.strip() == '':
        return None
    try:
        return float(value_str.replace(',', '.'))
    except ValueError:
        print(f"Warning: Could not convert '{value_str}' to float, using None instead.")
        return None

def init_db():
    print("Initializing database...") 
    import_to_postgresql()
    print("Database initialization finished.")