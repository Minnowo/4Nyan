









### Postgres Setup 

I'm using the portable installation from [postgresql.org](https://www.postgresql.org/download/) -> [zip archive](https://www.enterprisedb.com/download-postgresql-binaries). Extract the subfolders from **pgsql** into **backend/postgres/**. Then run [init_db.bat](setup/init_db.bat) which should set the data directory to **backend/postgres/bin/data**, after this run [start_postgres_server.bat](setup/start_postgres_server.bat) to begin running the server.

Then run pgadmin, and create a new server called **4Nyan-DB**. Set the hostname to localhost, the port to the same port as the value in **backend/postgres/bin/data/postgresql.conf** (change it if you want). I had to set the username to my windows username / the same value used in [constants.py](backend/bNyan/constants.py).

After making the server in pgadmin, create a new database called **4Nyan-DB** (same as server name). Since i'm using windows, I had to set the encoding to WIN1252.

After that the database is pretty much setup unless I forgot something.






