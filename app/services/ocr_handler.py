# app/services/ocr_service.py
import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
from datetime import datetime
from app.models.ocr_mapping import OCRMapping
from app import db
from pyzbar.pyzbar import decode


def preprocess_image(image_data):
    """Apply preprocessing to enhance OCR accuracy."""
    try:
        image = Image.open(io.BytesIO(image_data))
    except IOError:
        return {"error": "Unsupported image format"}, 400
        print("Processing OCR with image format:", image.format)

    image = image.convert('L')
    image = ImageEnhance.Contrast(image).enhance(2)
    image = image.filter(ImageFilter.SHARPEN)
    return image

def extract_text_from_image(image_data):
    image = Image.open(io.BytesIO(image_data))

    # Try both preprocessing methods and combine results
    results = []

    # Try printed text preprocessing
    printed_img = preprocess_printed_text(image)
    printed_result = pytesseract.image_to_string(
        printed_img,
        config='--psm 6',
        lang='eng'
    ).strip()

    # Try handwritten preprocessing
    handwritten_img = preprocess_handwritten(image)
    handwritten_result = pytesseract.image_to_string(
        handwritten_img,
        config='--psm 6 --oem 3',
        lang='eng'
    ).strip()

    # Compare results and take the one that seems more valid
    # Usually the better result will have:
    # - More recognized characters
    # - Fewer special characters
    # - More dictionary words
    def score_result(text):
        if not text:
            return 0
        # Count alphanumeric characters
        alpha_count = sum(c.isalnum() for c in text)
        # Count special characters (lower score for more special chars)
        special_count = sum(not c.isalnum() and not c.isspace() for c in text)
        # Basic score calculation
        return alpha_count - (special_count * 2)

    printed_score = score_result(printed_result)
    handwritten_score = score_result(handwritten_result)

    # Return the result with the better score
    if printed_score > handwritten_score:
        return printed_result
    return handwritten_result

def debug_image_processing(image_data):
    """Save steps of image processing for debugging"""
    processed = enhance_product_label(image_data)
    processed.save('debug_processed.png')
    return processed



def clean_ocr_text(text):
    """Clean OCR output text"""
    # Split into words
    words = text.split()

    # Filter words
    cleaned_words = []
    for word in words:
        # Remove words that are just special characters
        if not any(c.isalnum() for c in word):
            continue

        # Remove words that are too short
        if len(word) < 2:
            continue

        # Clean up the word
        cleaned_word = ''.join(c for c in word if c.isalnum() or c in ['-', '.', ' '])

        if cleaned_word:
            cleaned_words.append(cleaned_word)

    return ' '.join(cleaned_words)


def enhance_product_label(image_data):
    """Enhanced preprocessing specifically for product labels with dark backgrounds"""
    # Open the image from binary data
    image = Image.open(io.BytesIO(image_data))

    # Make image larger but not too large
    width, height = image.size
    image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)

    # Convert to grayscale
    gray = image.convert('L')

    # Increase contrast dramatically
    enhancer = ImageEnhance.Contrast(gray)
    high_contrast = enhancer.enhance(3.0)

    # Increase brightness to help with dark backgrounds
    brightness = ImageEnhance.Brightness(high_contrast)
    brightened = brightness.enhance(1.5)

    # Invert the image (turn dark background to light)
    inverted = ImageOps.invert(brightened)

    # Threshold to clean up the text
    threshold = inverted.point(lambda x: 0 if x < 140 else 255, '1')

    return threshold

def extract_barcode_from_image(image):
    """
    Extracts barcode information from a Pillow image object.
    """
    try:
        # Use pyzbar to decode barcodes from the image directly
        barcodes = decode(image)
        for barcode in barcodes:
            if barcode.type == "CODE128":  # Adjust this based on your barcode type
                return barcode.data.decode("utf-8")
        # Return None if no matching barcode is found
        return None
    except Exception as e:
        print(f"Error extracting barcode: {e}")
        return None
def correct_ocr(raw_text, corrected_text, serial_number):
    try:
        mapping = OCRMapping(
            raw_text=raw_text,
            corrected_text=corrected_text,
            serial_number=serial_number,
            last_used=datetime.utcnow()
        )
        db.session.add(mapping)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        print(f"Error saving correction: {e}")
        return {"error": "Failed to save correction"}

def save_ocr_correction(raw_text, corrected_text, serial_number):
    """Save OCR correction to improve future recognition."""
    try:
        mapping = OCRMapping(
            raw_text=raw_text,
            corrected_text=corrected_text,
            serial_number=serial_number,
            last_used=datetime.utcnow()
        )
        db.session.add(mapping)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        print(f"Error saving correction: {e}")
        return {"error": "Failed to save correction"}