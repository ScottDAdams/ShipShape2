import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from app.models.item import Item
from app.models.photo import Photo


# Load environment variables from .env file
load_dotenv(dotenv_path='.env')

# Get the DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize the database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Define directories
PHOTO_DIR = 'app/static/bulkphotos'


def import_photos():
    session = Session()
    try:
        # Iterate through files in the bulk photos directory
        for filename in os.listdir(PHOTO_DIR):
            # Skip non-image files
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            # Extract serial number from filename (e.g., 2100 from 2100.jpg or 2100.1.jpg)
            serial_number = filename.split('.')[0]

            # Query items with this serial number
            items = session.query(Item).filter(Item.serial_number == serial_number).all()

            if not items:
                print(f"No item found for serial number: {serial_number}")
                continue

            # Read image data as binary
            with open(os.path.join(PHOTO_DIR, filename), 'rb') as img_file:
                image_data = img_file.read()

            # Process each item matching the serial number
            for item in items:
                # Create a new Photo record for each item
                new_photo = Photo(
                    item_id=item.id,
                    image_data=image_data  # Store binary data here
                )
                session.add(new_photo)

            print(f"Assigned photo '{filename}' to {len(items)} item(s) with serial number {serial_number}")

        # Commit the transaction
        session.commit()
        print("Photo import completed successfully.")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        session.rollback()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        session.close()


if __name__ == '__main__':
    import_photos()
