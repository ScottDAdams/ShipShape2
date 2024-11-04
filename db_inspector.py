# db_inspector.py
from dotenv import load_dotenv
from flask import Flask
from app.database import db
from app.models import Item, Category, Location, Photo
import os
from sqlalchemy import text

load_dotenv()


def create_minimal_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def inspect_database():
    app = create_minimal_app()

    with app.app_context():
        print("\nDatabase Tables:")
        print("-" * 50)

        # Get all tables using SQLAlchemy's updated execution API
        with db.engine.connect() as connection:
            # Get tables
            tables_result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))

            tables = tables_result.fetchall()

            if not tables:
                print("No tables found in database.")
                return

            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                print("-" * 20)

                # Get columns for each table
                columns_result = connection.execute(text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """), {"table_name": table_name})

                columns = columns_result.fetchall()

                for column in columns:
                    nullable = "NULL" if column[2] == "YES" else "NOT NULL"
                    print(f"{column[0]}: {column[1]} ({nullable})")


if __name__ == "__main__":
    inspect_database()