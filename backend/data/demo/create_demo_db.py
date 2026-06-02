import os
import sqlite3 # Just in case we need date helpers, but duckdb works directly
from datetime import datetime, timedelta
import duckdb

def main():
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, "ecommerce.duckdb")
    ddl_path = os.path.join(db_dir, "ecommerce_schema.sql")

    # Remove existing db if any to rebuild fresh
    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"Connecting to DuckDB at {db_path}...")
    con = duckdb.connect(db_path)

    # Read and execute DDL
    print("Creating tables...")
    with open(ddl_path, "r") as f:
        ddl_sql = f.read()
    con.execute(ddl_sql)

    # Seed Regions
    print("Seeding regions...")
    regions = [
        ("REG_NORTH", "North America", "John Doe"),
        ("REG_EUROPE", "Europe", "Marie Curie"),
        ("REG_ASIA", "Asia-Pacific", "Kenji Sato"),
    ]
    con.executemany("INSERT INTO regions VALUES (?, ?, ?)", regions)

    # Seed Customers
    print("Seeding customers...")
    customers = [
        ("CUST_001", "Asha Patel", "asha.patel@example.com", "VIP", "REG_ASIA", "2025-06-15 10:00:00"),
        ("CUST_002", "Rahul Mehta", "rahul.mehta@example.com", "Corporate", "REG_ASIA", "2025-08-20 14:30:00"),
        ("CUST_003", "Sarah Connor", "sarah.connor@example.com", "Retail", "REG_NORTH", "2025-09-01 09:15:00"),
        ("CUST_004", "David Smith", "david.smith@example.com", "Retail", "REG_NORTH", "2025-11-12 16:45:00"),
        ("CUST_005", "Emma Watson", "emma.watson@example.com", "VIP", "REG_EUROPE", "2025-12-05 11:20:00"),
        ("CUST_006", "Jean Dupont", "jean.dupont@example.com", "Corporate", "REG_EUROPE", "2026-01-10 08:00:00"),
        ("CUST_007", "No Order Nelson", "nelson@example.com", "Retail", "REG_NORTH", "2026-02-15 12:00:00"), # Customer with no orders
    ]
    con.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers)

    # Seed Products
    print("Seeding products...")
    products = [
        ("PROD_001", "Developer Laptop", "Electronics", 1200.00, 50),
        ("PROD_002", "Mechanical Keyboard", "Electronics", 150.00, 200),
        ("PROD_003", "Ergonomic Chair", "Office", 350.00, 80),
        ("PROD_004", "Water Bottle", "Home", 25.00, 500),
        ("PROD_005", "Coffee Mug", "Home", 15.00, 1000),
        ("PROD_006", "Notebook", "Office", 5.00, 1500),
    ]
    con.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)

    # Seed Orders (spanning Jan 2026 to May 2026)
    print("Seeding orders...")
    orders = [
        # Q1 2026 (Jan - Mar)
        ("ORD_001", "CUST_001", "2026-01-15 10:30:00", 1230.00, "Completed"),
        ("ORD_002", "CUST_002", "2026-01-20 15:45:00", 300.00, "Completed"),
        ("ORD_003", "CUST_003", "2026-02-05 09:00:00", 50.00, "Completed"),
        ("ORD_004", "CUST_004", "2026-02-10 11:20:00", 1200.00, "Completed"),
        ("ORD_005", "CUST_005", "2026-03-01 14:00:00", 1550.00, "Completed"),
        ("ORD_006", "CUST_001", "2026-03-12 16:30:00", 150.00, "Completed"),
        ("ORD_007", "CUST_006", "2026-03-25 10:15:00", 350.00, "Completed"),
        
        # Last Month (May 2026)
        ("ORD_008", "CUST_001", "2026-05-02 11:00:00", 1375.00, "Completed"),
        ("ORD_009", "CUST_002", "2026-05-05 13:40:00", 1200.00, "Completed"),
        ("ORD_010", "CUST_003", "2026-05-12 09:30:00", 175.00, "Completed"),
        ("ORD_011", "CUST_005", "2026-05-18 16:00:00", 40.00, "Completed"),
        ("ORD_012", "CUST_006", "2026-05-22 10:00:00", 1230.00, "Completed"),
        ("ORD_013", "CUST_001", "2026-05-28 15:00:00", 15.00, "Completed"),
    ]
    con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

    # Seed Order Items
    print("Seeding order items...")
    order_items = [
        # ORD_001
        ("ITEM_001", "ORD_001", "PROD_001", 1, 1200.00),
        ("ITEM_002", "ORD_001", "PROD_005", 2, 15.00),
        
        # ORD_002
        ("ITEM_003", "ORD_002", "PROD_002", 2, 150.00),
        
        # ORD_003
        ("ITEM_004", "ORD_003", "PROD_004", 2, 25.00),
        
        # ORD_004
        ("ITEM_005", "ORD_004", "PROD_001", 1, 1200.00),
        
        # ORD_005
        ("ITEM_006", "ORD_005", "PROD_001", 1, 1200.00),
        ("ITEM_007", "ORD_005", "PROD_003", 1, 350.00),
        
        # ORD_006
        ("ITEM_008", "ORD_006", "PROD_002", 1, 150.00),
        
        # ORD_007
        ("ITEM_009", "ORD_007", "PROD_003", 1, 350.00),
        
        # ORD_008 (Asha bought laptop, ergonomic chair, and coffee mug)
        ("ITEM_010", "ORD_008", "PROD_001", 1, 1200.00),
        ("ITEM_011", "ORD_008", "PROD_002", 1, 150.00),
        ("ITEM_012", "ORD_008", "PROD_005", 1, 15.00),
        ("ITEM_013", "ORD_008", "PROD_006", 2, 5.00),
        
        # ORD_009 (Rahul bought developer laptop)
        ("ITEM_014", "ORD_009", "PROD_001", 1, 1200.00),
        
        # ORD_010 (Sarah bought mechanical keyboard and water bottle)
        ("ITEM_015", "ORD_010", "PROD_002", 1, 150.00),
        ("ITEM_016", "ORD_010", "PROD_004", 1, 25.00),
        
        # ORD_011 (Emma bought water bottle and coffee mug)
        ("ITEM_017", "ORD_011", "PROD_004", 1, 25.00),
        ("ITEM_018", "ORD_011", "PROD_005", 1, 15.00),
        
        # ORD_012 (Jean bought developer laptop and coffee mug)
        ("ITEM_019", "ORD_012", "PROD_001", 1, 1200.00),
        ("ITEM_020", "ORD_012", "PROD_005", 2, 15.00),
        
        # ORD_013 (Asha bought coffee mug)
        ("ITEM_021", "ORD_013", "PROD_005", 1, 15.00),
    ]
    con.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items)

    con.commit()
    con.close()
    print("Database built successfully!")

if __name__ == "__main__":
    main()
