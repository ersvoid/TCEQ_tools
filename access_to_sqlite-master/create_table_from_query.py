import sqlite3
import csv

def create_sql_table(s, f, j, o, n, d, t, st=""):
    if st == "":
        st = s
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("SELECT {} "
              "FROM {} "
              "INNER JOIN {} "
              "ON {}".format(s, f, j, o))
    fieldnames = n.split(", ")
    values = len(fieldnames)
    with open('temp_join.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        print("Writing to CSV file...")
        for row in c.fetchall():
            writer.writerow(row)
        print("Writing complete.")
    c.close()
    conn.close()
    print("Connection closed.")
    print("Query closed.")
    print("Connecting to SQLite database...")
    con = sqlite3.connect("{}.db".format(d))
    cur = con.cursor()
    print("Connection established to {} database".format(d))
    print("Creating table...")
    cur.execute("CREATE TABLE {} ({})".format(t, st))
    print("Created table: {}".format(t))
    print("Importing CSV file...")
    with open(r'temp_join.csv', 'rt') as fin:
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin)
        to_db = []
        for i in dr:
            lst = []
            for field in fieldnames:
                lst.append(i[field])
            to_db.append(lst)

    def val(v):
        lst = []
        for a in range(v):
            lst.append('?')
        return ", ".join(lst)
    cur.executemany("INSERT INTO " + t + " (" + n + ") VALUES (" + val(values) + ")", to_db)
    con.commit()
    print("Import complete.")
    cur.close()
    con.close()
    print("Connection closed.")
