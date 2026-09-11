from cassandra.cluster import Cluster
import uuid



# ==============================
# CQL Statements
# ==============================
CREATE_KEYSPACE = ""
CREATE_TABLE_MOVIE_BY_TITLE = ""
CREATE_TABLE_MOVIE_BY_GENRE = ""
INSERT_MOVIE_TITLE = ""
INSERT_MOVIE_GENRE = ""
DELETE_MOVIE_TITLE = ""
DELETE_MOVIE_GENRE = ""
SELECT_BY_TITLE = ""
SELECT_BY_GENRE = ""

# ==============================
# Funciones base
# ==============================
def create_keyspace_and_tables(session):
    CREATE_KEYSPACE = """
    CREATE KEYSPACE IF NOT EXISTS movies
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}  
    """
    session.execute(CREATE_KEYSPACE)
    session.set_keyspace("movies")
    print("Keyspace movies creado y seleccionado")

    CREATE_TABLE_MOVIES_BY_TITLE = """
    CREATE TABLE IF NOT EXISTS movies_by_title(
    movie_id UUID, title TEXT, release_year INT, genre TEXT, rating FLOAT, director TEXT, 
    PRIMARY KEY(title, release_year))
    """

    stmt = session.prepare(CREATE_TABLE_MOVIES_BY_TITLE)
    session.execute(stmt)
    print("Tabla movies_by_title creada")

    CREATE_TABLE_MOVIES_BY_GENRE = """
    CREATE TABLE IF NOT EXISTS movies_by_genre(
    movie_id UUID, title TEXT, release_year INT, genre TEXT, rating FLOAT, director TEXT, 
    PRIMARY KEY(genre, rating))
    """

    stmt = session.prepare(CREATE_TABLE_MOVIES_BY_GENRE)
    session.execute(stmt)
    print("Tabla movies_by_genre creada")
    

def insert_movie(session, title, year, director, genre, rating):
    INSERT_MOVIE = """
    INSERT INTO movies_by_title(
    movie_id, title, release_year, genre, rating, director)
    VALUES(?,?,?,?,?,?)
    """

    movie_id = uuid.uuid4()
    stmt = session.prepare(INSERT_MOVIE)
    session.execute(stmt, (movie_id, title, year, genre, rating, director))
    print("Pelicula agregada")

    INSERT_MOVIE2 = """
    INSERT INTO movies_by_genre(
    movie_id, title, release_year, genre, rating, director)
    VALUES(?,?,?,?,?,?)
    """

    movie_id = uuid.uuid4()
    stmt = session.prepare(INSERT_MOVIE2)
    session.execute(stmt, (movie_id, title, year, genre, rating, director))
    print("Pelicula agregada")


def query_by_title(session, title, year):
    if year == 0:

        SELECT_BY_TITLE = """
        SELECT * 
        FROM movies_by_title 
        WHERE title = ?;
        """

        query = session.prepare(SELECT_BY_TITLE)
        rows = session.execute(query, (title, )) 

        for row in rows:
            print(row)
    else:
        SELECT_BY_TITLE = """
        SELECT * 
        FROM movies_by_title 
        WHERE title = ? AND release_year = ?;
        """

        query = session.prepare(SELECT_BY_TITLE)
        rows = session.execute(query, (title, year)) 

        for row in rows:
            print(row)


def query_by_genre(session, genre):

    SELECT_BY_GENRE = """
    SELECT *
    FROM movies_by_genre
    WHERE genre = ?
    ORDER BY rating DESC;
    """

    query = session.prepare(SELECT_BY_GENRE)
    rows = session.execute(query, (genre, ))

    for row in rows:
        print(row)


def update_movie_director(session, title, genre, new_director):

    SELECT_MOVIE = """
    SELECT *
    FROM movies_by_title
    WHERE title = ?;
    """

    query = session.prepare(SELECT_MOVIE)
    rows = session.execute(query, (title, ))

    for row in rows:
        year = row.release_year
        rating = row.rating 

    UPDATE_MOVIE = """
    UPDATE movies_by_title
    SET director = ?
    WHERE title = ? AND release_year = ?;
    """

    query = session.prepare(UPDATE_MOVIE)
    session.execute(query, (new_director, title, year))

    UPDATE_MOVIE2 = """
    UPDATE movies_by_genre
    SET director = ?
    WHERE genre = ? AND rating = ?
    """

    query = session.prepare(UPDATE_MOVIE2)
    session.execute(query, (new_director, genre, rating))
    print("Director actualizado en ambas tablas")


def delete_movie(session, title, genre, rating, release_year):
    DELETE_MOVIE = """
    DELETE FROM movies_by_title
    WHERE title = ? AND release_year = ?;
    """

    query = session.prepare(DELETE_MOVIE)
    session.execute(query, (title, release_year))

    DELETE_MOVIE2 = """
    DELETE FROM movies_by_genre
    WHERE genre = ? AND rating = ?;
    """

    query = session.prepare(DELETE_MOVIE2)
    session.execute(query, (genre, rating))

    print("Pelicula eliminada con exito de ambas tablas")


# ==============================
# Menú
# ==============================
def main():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    create_keyspace_and_tables(session)

    while True:
        print("\n=== Movie Database Menu ===")
        print("1. Insertar película")
        print("2. Consultar por título")
        print("3. Consultar por género")
        print("4. Actualizar director")
        print("5. Eliminar una pelicula")
        print("0. Salir")
        choice = input("Seleccione opción: ")

        if choice == "1":
            title = input("Título: ")
            year = int(input("Año: "))
            director = input("Director: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            insert_movie(session, title, year, director, genre, rating)
        elif choice == "2":
            title = input("Título: ")
            year = input("Año (presiona enter si no sabes el año): ")
            if year == "":
                query_by_title(session, title, 0)
            else:
                query_by_title(session, title, int(year))
        elif choice == "3":
            genre = input("Género: ")
            query_by_genre(session, genre)
        elif choice == "4":
            title = input("Título: ")
            genre = input("Género: ")
            new_director = input("Nuevo Director: ")
            update_movie_director(session, title, genre, new_director)
        elif choice == "5":
            # Eliminar de movie_by_title -> title, release_year
            # Eliminar de movie_by_genre -> genre, rating
            title = input("Título: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            release_year = int(input("Año: "))
            delete_movie(session, title, genre, rating, release_year)
        elif choice == '0':
            print("Cerrando conexion...")
            session.shutdown()
            cluster.shutdown()
            break
        else:
            print("Opción inválida")
            break

if __name__ == "__main__":
    main()