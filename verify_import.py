def verify_data(db_connection_string):
    """Verify the imported data for integrity"""
    engine = create_engine(db_connection_string)
    conn = engine.raw_connection()
    cur = conn.cursor()

    # Check for serial numbers in multiple locations
    cur.execute("""
        SELECT serial_number, COUNT(DISTINCT boat_section_id) as locations,
               array_agg(DISTINCT boat_section_id) as section_ids
        FROM items
        WHERE serial_number IS NOT NULL
        GROUP BY serial_number
        HAVING COUNT(DISTINCT boat_section_id) > 1
    """)

    duplicates = cur.fetchall()
    if duplicates:
        print("\nWarning: Found serial numbers in multiple locations:")
        for dup in duplicates:
            print(f"Serial number {dup[0]} found in {dup[1]} locations")

    # Verify all items have valid boat sections
    cur.execute("""
        SELECT COUNT(*)
        FROM items
        WHERE boat_section_id IS NULL
    """)

    missing_sections = cur.fetchone()[0]
    if missing_sections:
        print(f"\nWarning: {missing_sections} items have no boat section assigned")

    # Check photo links
    cur.execute("""
        SELECT COUNT(*)
        FROM photos p
        LEFT JOIN items i ON p.item_id = i.id
        WHERE i.id IS NULL
    """)

    orphaned_photos = cur.fetchone()[0]
    if orphaned_photos:
        print(f"\nWarning: {orphaned_photos} photos are not linked to valid items")

    cur.close()
    conn.close()