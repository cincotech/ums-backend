import MySQLdb

try:
    # Connect to MySQL
    db = MySQLdb.connect(
        host="23.235.216.192",
        user="btcshulevgfhnehg_idris",
        password="XvR3lKKHJaTh",
        database="btcshulevgfhnehg_ums",
        port=3306,
    )

    cursor = db.cursor()
    print("Connected to MySQL using mysqlclient")

    # Tables to drop
    tables_to_drop = ["backup_records", "audit_logs"]

    # Drop each table
    for table in tables_to_drop:
        drop_sql = f"DROP TABLE IF EXISTS `{table}`;"
        cursor.execute(drop_sql)
        db.commit()
        print(f"Dropped table: {table}")

except Exception as e:
    print("Error:", e)

finally:
    if "db" in locals():
        cursor.close()
        db.close()
        print("MySQL connection closed")
