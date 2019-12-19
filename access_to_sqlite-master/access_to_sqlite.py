import pyodbc
import csv
import sqlite3

def import_access_to_sqlite(select, access_table, db, table_name, select_terms=""):
    # MS ACCESS DB CONNECTION
    if select_terms == "":
        select_terms = select
    pyodbc.lowercase = False
    print("Connecting to Access Database...")
    conn = pyodbc.connect(
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
        r"Dbq=file.accdb;")
    print("Connection established.")
    # OPEN CURSOR AND EXECUTE SQL
    print("Querying data...")
    cur = conn.cursor()
    cur.execute("SELECT {} FROM {}".format(select, access_table))
    print("Query complete.")
    # OPEN CSV AND ITERATE THROUGH RESULTS
    print("Opening CSV file...")
    fieldnames = select.split()
    values = len(fieldnames)
    with open('test.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        print("Writing to CSV file...")
        for row in cur.fetchall():
            writer.writerow(row)
        print("Writing complete.")
    cur.close()
    conn.close()
    print("Connection closed.")
    print("Query closed.")
    print("Connecting to SQLite database...")
    con = sqlite3.connect("{}.db".format(db))
    cur = con.cursor()
    print("Connection established to {} database".format(db))
    print("Creating table...")
    cur.execute("CREATE TABLE {} ({});".format(table_name, select_terms))
    print("Created table: {}".format(table_name))
    print("Importing CSV file...")
    with open(r'test.csv', 'rt') as fin:
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin)
        to_db = []
        for i in dr:
            lst = []
            for field in fieldnames:
                lst.append(i[field])
            to_db.append(lst)

    def val(values):
        lst = []
        for n in range(values):
            lst.append('?')
        return ", ".join(lst)
    cur.executemany("INSERT INTO {} ({}) VALUES ({});".format(table_name, select, val(values)), to_db)
    con.commit()
    print("Import complete.")
    cur.close()
    con.close()
    print("Connection closed.")
