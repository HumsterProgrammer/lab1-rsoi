import psycopg

def db_get_cursor():
	conn = psycopg2.connect(database="persons",
                host="db_host",
                user="program",
                password="test",
                port="db_port")
	cursor = conn.cursor()
	return cursor

def db_create_table(cursor):
	cursor.execute("""CREATE TABLE persons (
		ID INTEGER PRIMARY KEY ,
		Name varchar(30),
		Age INTEGER,
		Address varchar(30),
		Work varchar(30)
	);
	""") 

def db_get_persons(cursor):
	cursor.execute("SELECT * FROM persons")
	return cursor.fetchall()

def get_by_id():
	return None
