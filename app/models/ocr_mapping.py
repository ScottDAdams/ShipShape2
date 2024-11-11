# models/ocr_mapping.py
from app.database import db
from datetime import datetime


class OCRMapping(db.Model):
    __tablename__ = 'ocr_mappings'

    id = db.Column(db.Integer, primary_key=True)
    raw_text = db.Column(db.Text, nullable=False)  # Raw OCR output
    corrected_text = db.Column(db.String(255), nullable=False)  # Final corrected text
    serial_number = db.Column(db.String(255), nullable=True)  # Associated barcode/serial if any
    times_matched = db.Column(db.Integer, default=0)  # Track successful matches
    last_used = db.Column(db.DateTime)  # Track when this mapping was last used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def find_best_match(raw_text):
        """Find best matching previous correction"""
        mappings = OCRMapping.query.all()
        best_match = None
        best_score = 0

        for mapping in mappings:
            score = OCRMapping.calculate_similarity(raw_text, mapping.raw_text)
            if score > best_score and score > 0.7:  # Require 70% similarity
                best_score = score
                best_match = mapping

        if best_match:
            best_match.times_matched += 1
            best_match.last_used = datetime.utcnow()
            db.session.commit()
            return best_match.corrected_text

        return None

    @staticmethod
    def calculate_similarity(text1, text2):
        """Calculate similarity between two texts"""
        # Convert to sets of words
        words1 = set(w.lower() for w in text1.split() if len(w) >= 3)
        words2 = set(w.lower() for w in text2.split() if len(w) >= 3)

        if not words1 or not words2:
            return 0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0