# access_to_sqlite
Convert MS Access to SQLITE3
<br>
<br>
<h1><b>Import ACCESS DATABASE into SQLITE using Python</b></h1><br>
<br>
Function: import_access_to_sqlite(select, access_table, db, table_name, select_terms="")<br>
<br>
<b>Select:</b> Statement String Called with SQL Select<br>
<b>Access_table:</b> Table name in Access to import from<br>
<b>DB:</b> Database name<br>
<b>Table_name:</b> New table name in SQLITE<br>
<b>Select_terms:</b> Statement string called with SQL Create Table to define primary key, varchar, etc. If left empty, function will define as equal to 'select' variable.
<br><br><br>
Function takes a MS Access database file and converts into a SQLite database using the pyodbc, csv, and sqlite3 modules in Python.
