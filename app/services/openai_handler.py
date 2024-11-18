import json
import re
from openai import OpenAI

client = OpenAI()


def analyze_image_text(image_data, prompt):
    try:
        # Prepare the messages content with base64 encoded image
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]
            }
        ]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300
        )

        # Log raw response
        print("Raw response from OpenAI:", response)

        # Extract content
        content = response.choices[0].message.content.strip()
        print("Extracted content before processing:", content)

        # Remove markdown code blocks if present
        content = content.replace("```json", "").replace("```", "").strip()

        # Use regex to find JSON content within curly braces
        json_match = re.search(r'\{.*\}', content, re.DOTALL)

        if json_match:
            # Extract and clean up matched JSON string
            json_content = json_match.group(0).strip()
            print("Extracted JSON content:", json_content)

            # Parse the JSON string into a Python dictionary
            data = json.loads(json_content)
            return data
        else:
            print("No JSON content found in response.")
            return {"error": "Failed to extract JSON content from OpenAI response"}

    except json.JSONDecodeError as e:
        print("Error decoding JSON from OpenAI response:", e)
        return {"error": f"JSON decode error: {str(e)}"}
    except Exception as e:
        print(f"Error during OpenAI call: {str(e)}")
        return {"error": f"General error: {str(e)}"}
