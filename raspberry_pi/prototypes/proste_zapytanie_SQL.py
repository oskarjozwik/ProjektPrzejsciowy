import mysql.connector
import sys # Pobranie wartosci z terminala jako klucz

id_zapytanie = sys.argv[1]

config = {
    'user': 'tapedeck',
    'password': 'Jof_159',
    'host': '192.168.0.109',
    'database': 'Tasmociag'
}

def db_query(id_paczki):
    try:
        db = mysql.connector.connect(**config)
        kursor = db.cursor(dictionary=True) # Traktujemy kazde pole jak slownik, latwosc odczytu

        query = "SELECT * FROM Paczki WHERE id_paczki = %s"
        kursor.execute(query, (id_paczki,))
        result = kursor.fetchone()

        kursor.close()
        db.close()
        return result

    except Exception as e:
        print(f"Error: {e}")
        return None


paczka = db_query(id_zapytanie)

if paczka:
    print(f"Paczka: {paczka['id_paczki']}")
    print(f"Data nadania: {paczka['data_nadania']}")
    print(f"Miejsce docelowe: {paczka['miejsce_docelowe']}")
