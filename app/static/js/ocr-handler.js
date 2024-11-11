// static/js/ocr-handler.js
class OCRHandler {
    constructor() {
        this.rawOCRText = '';
    }

    async handleOCRResult(result) {
        // Store the raw OCR text
        this.rawOCRText = result.raw_text;

        // Set form field values
        document.getElementById('serial_number').value = result.serial_number || '';
        document.getElementById('name').value = result.name || '';

        // Add visual feedback if using learned text
        if (result.is_learned) {
            const nameInput = document.getElementById('name');
            const existingInfo = nameInput.parentNode.querySelector('.ocr-info');
            if (!existingInfo) {
                const infoDiv = document.createElement('div');
                infoDiv.className = 'ocr-info ocr-learned';
                infoDiv.textContent = '✓ Using learned text recognition';
                nameInput.parentNode.appendChild(infoDiv);
            }
        }
    }

    async saveCorrection(formElement) {
        if (!this.rawOCRText) return;

        const correctedText = formElement.querySelector('#name').value;
        const serialNumber = formElement.querySelector('#serial_number').value;

        try {
            const response = await fetch('/mobile/ocr/correct', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    raw_text: this.rawOCRText,
                    corrected_text: correctedText,
                    serial_number: serialNumber
                })
            });

            if (!response.ok) {
                console.error('Failed to save OCR correction');
            }
        } catch (error) {
            console.error('Error saving OCR correction:', error);
        }
    }
}