import psycopg

def db_get_cursor():
	conn = psycopg2.connect(database="persons",
                host="db_host",
                user="program",
                password="test",
                port="5432")
	cursor = conn.cursor()
	return cursor

def db_create_table(cursor):
	cursor.execute("""CREATE TABLE persons (
		id INTEGER PRIMARY KEY ,
		name varchar(30),
		age INTEGER,
		address varchar(30),
		work varchar(30)
	);
	""")
	return cursor.pgresult is not None

def db_get_persons(cursor):
	cursor.execute("SELECT * FROM persons")
	return cursor.pgresult is not None, cursor.fetchall()

def db_get_by_id(cursor, personId):
	cursor.execute("SELECT * FROM persons WHERE id=%s", (personId, ))
	return cursor.pgresult is not None, cursor.fetchall()

def db_post_persons(cursor, name, age, address, work):
	cursor.execute("INSERT INTO persons (Name, Age, Address, Work) VALUES (%s, %s, %s, %s);", (name, age, address, work, ))
	return cursor.pgresult is not None, cursor.fetchall()

def db_update_persons(cursor, personId, name, age, address, work):
	cursor.execute("UPDATE persons SET Name = %s, Age = %s, Address = %s, Work = %s WHERE id = %s;", (name, age, address, work, personId, ))
	return cursor.pgresult is not None, cursor.fetchall()

def db_delete_persons(cursor, personId):
	cursor.execute("DELETE FROM persons WHERE id = %s", (personId, ))
	return cursor.pgresult is not None, cursor.fetchall()
	

