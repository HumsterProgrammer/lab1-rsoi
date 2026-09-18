import psycopg2
from psycopg2.extras import RealDictCursor


def db_get_cursor():
    conn = psycopg2.connect(
        database="persons",
        host="db_host",
        user="program",
        password="test",
        port="5432"
    )
    return conn.cursor(cursor_factory=RealDictCursor)


def db_create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id SERIAL PRIMARY KEY,
            name VARCHAR(30) NOT NULL,
            age INTEGER,
            address VARCHAR(30),
            work VARCHAR(30)
        );
    """)
    cursor.connection.commit()
    return True


def db_get_persons(cursor):
    cursor.execute("""
        SELECT id, name, age, address, work
        FROM persons
        ORDER BY id;
    """)
    rows = cursor.fetchall()
    return True, [dict(row) for row in rows]


def db_get_by_id(cursor, personId):
    cursor.execute("""
        SELECT id, name, age, address, work
        FROM persons
        WHERE id = %s;
    """, (personId,))
    row = cursor.fetchone()
    if row is None:
        return False, None
    return True, dict(row)


def db_post_persons(cursor, name, age=None, address=None, work=None):
    cursor.execute("""
        INSERT INTO persons (name, age, address, work)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, age, address, work;
    """, (name, age, address, work))
    row = cursor.fetchone()
    cursor.connection.commit()
    if row is None:
        return False, None
    return True, dict(row)


def db_update_persons(cursor, personId, data):
    allowed = {"name", "age", "address", "work"}
    fields = {key: value for key, value in data.items() if key in allowed}

    if not fields:
        return False, None

    set_part = ", ".join(f"{key} = %s" for key in fields)
    values = list(fields.values()) + [personId]

    cursor.execute(f"""
        UPDATE persons
        SET {set_part}
        WHERE id = %s
        RETURNING id, name, age, address, work;
    """, values)

    row = cursor.fetchone()
    cursor.connection.commit()

    if row is None:
        return False, None
    return True, dict(row)


def db_delete_persons(cursor, personId):
    cursor.execute("""
        DELETE FROM persons
        WHERE id = %s
        RETURNING id;
    """, (personId,))
    row = cursor.fetchone()
    cursor.connection.commit()
    return row is not None
