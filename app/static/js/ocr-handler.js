document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const serialNumberInput = document.getElementById('serial_number');
    const nameInput = document.getElementById('name');
    const partNumberInput = document.getElementById('part_number');
    const imageInput = document.getElementById('image');
    const openaiButton = document.getElementById('ocr-button');

    openaiButton.addEventListener('click', async function() {
        if (imageInput.files.length > 0) {
            const formData = new FormData();
            formData.append('image', imageInput.files[0]);

            try {
                const response = await fetch('https://whippet-robust-oarfish.ngrok-free.app/inventory/process_openai', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const result = await response.json();
                    if (result.serial_number) serialNumberInput.value = result.serial_number;
                    if (result.name) nameInput.value = result.name;
                    if (result.part_number) partNumberInput.value = result.part_number;
                } else {
                    console.error('Received non-JSON response:', await response.text());
                    alert('Unexpected server response. Please check if the endpoint is correct.');
                }
            } catch (error) {
                console.error('OpenAI processing error:', error);
                alert('Failed to process with OpenAI. Please check the server or endpoint URL.');
            }
        } else {
            alert('Please upload an image first.');
        }
    });
});
