# database_connection.py
from dotenv import load_dotenv
from flask import Flask
from app.database import db
import os

# Load environment variables
load_dotenv()


def create_minimal_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def test_db_connection():
    print("Creating minimal Flask app...")
    app = create_minimal_app()

    print("\nTesting database connection...")
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

    try:
        with app.app_context():
            # Try to connect
            db.engine.connect()
            print("✅ Successfully connected to database!")

            # Try to create tables
            print("\nAttempting to create database tables...")
            db.create_all()
            print("✅ Successfully created tables!")
            return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    test_db_connection()