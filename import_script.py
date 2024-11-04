import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from datetime import datetime


def clean_boat_section(name):
    """Standardize boat section names"""
    if pd.isna(name) or not name:
        return None
    return str(name).strip().lower().capitalize()


def clean_numeric(value):
    """Handle numeric values, return None if invalid"""
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def import_data(csv_file, db_connection_string):
    """Import CSV data into the database"""
    print("Reading CSV file...")
    df = pd.read_csv(csv_file)

    # Create database connection
    engine = create_engine(db_connection_string)
    conn = engine.raw_connection()
    cur = conn.cursor()

    # Process boat sections
    print("Processing boat sections...")
    section_ids = {}

    # First get all existing boat sections
    cur.execute("SELECT id, name FROM boat_sections")
    existing_sections = {name.lower(): id for id, name in cur.fetchall()}

    # Process new sections
    for section in df['Boat Section'].unique():
        if pd.notna(section):
            section = clean_boat_section(section)
            if section.lower() in existing_sections:
                # Use existing section ID
                section_ids[section] = existing_sections[section.lower()]
            else:
                # Insert new section
                cur.execute(
                    "INSERT INTO boat_sections (name) VALUES (%s) RETURNING id",
                    (section,)
                )
                section_ids[section] = cur.fetchone()[0]
                existing_sections[section.lower()] = section_ids[section]

    conn.commit()

    print("Importing items...")
    imported_count = 0
    photo_count = 0

    # Import all items
    for _, row in df.iterrows():
        boat_section = clean_boat_section(row['Boat Section'])

        cur.execute("""
            INSERT INTO items 
                (name, boat_section_id, shelf, box, serial_number, quantity, part_number)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            row['Item Name'],
            section_ids.get(boat_section),
            str(row['Shelf']) if pd.notna(row['Shelf']) else None,
            str(row['Box']) if pd.notna(row['Box']) else None,
            str(row['Serial Number']) if pd.notna(row['Serial Number']) else None,
            clean_numeric(row['Quantity']),
            str(row['Part Number']) if pd.notna(row['Part Number']) else None
        ))

        item_id = cur.fetchone()[0]
        imported_count += 1

        # Handle photos
        for photo_col in ['Photos1', 'Photos2']:
            if pd.notna(row[photo_col]) and str(row[photo_col]).strip():
                cur.execute("""
                    INSERT INTO photos (item_id, url)
                    VALUES (%s, %s)
                """, (item_id, str(row[photo_col]).strip()))
                photo_count += 1

        # Commit every 100 records
        if imported_count % 100 == 0:
            conn.commit()
            print(f"Imported {imported_count} items...")

    # Final commit
    conn.commit()

    print("\nImport Summary:")
    print(f"- {imported_count} items imported")
    print(f"- {photo_count} photos linked")
    print(f"- Using {len(section_ids)} boat sections")

    # Show potential conflicts for future resolution
    print("\nPotential conflicts to resolve later:")
    cur.execute("""
        SELECT serial_number, COUNT(*) as count
        FROM items
        WHERE serial_number IS NOT NULL
        GROUP BY serial_number
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)

    conflicts = cur.fetchall()
    if conflicts:
        print(f"Found {len(conflicts)} serial numbers with multiple entries:")
        for serial_number, count in conflicts[:5]:
            print(f"- Serial {serial_number}: {count} entries")
        if len(conflicts) > 5:
            print(f"... and {len(conflicts) - 5} more")

    cur.close()
    conn.close()


if __name__ == "__main__":
    # Update these with your actual connection details
    DB_CONNECTION = "postgresql://postgres.neizqytwgtiveuppldxc:NE#K&o9F&DtXfFgL@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    CSV_FILE = "inventory.csv"

    try:
        import_data(CSV_FILE, DB_CONNECTION)
    except Exception as e:
        print(f"Error during import: {str(e)}")