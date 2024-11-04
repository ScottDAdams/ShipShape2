# app/services/validation_service.py
from typing import List, Dict


class ValidationService:
    def validate_item(self, item_data: Dict) -> List[str]:
        errors = []

        # Required fields
        required_fields = ['serial_number', 'name', 'quantity']
        for field in required_fields:
            if not item_data.get(field):
                errors.append(f"{field} is required")

        # Format validations
        if item_data.get('serial_number'):
            if not self._is_valid_serial(item_data['serial_number']):
                errors.append("Invalid serial number format")

        # Quantity validation
        if item_data.get('quantity'):
            try:
                qty = int(item_data['quantity'])
                if qty < 0:
                    errors.append("Quantity cannot be negative")
            except ValueError:
                errors.append("Quantity must be a number")

        return errors