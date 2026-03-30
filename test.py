import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=BarangayDB;Trusted_Connection=yes;"
)
print("Connected successfully!")