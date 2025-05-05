import os
import httpx
import json
import logging
from dotenv import load_dotenv
from httpx import TimeoutException  # Corrected import

# Load environment variables
load_dotenv()

AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_API_KEY
}

# Setup logging
logging.basicConfig(level=logging.INFO)

async def parse_resume_with_openai(resume_text: str) -> dict:
    try:
        if not AZURE_API_ENDPOINT or not AZURE_API_KEY:
            raise ValueError("Azure OpenAI API key or endpoint not configured.")

        # Define system prompt
        system_prompt = (
            "You are an intelligent resume parser. Extract structured data from resume text. "
            "Return only a JSON object with the following keys: name, email, phone, skills (list),Education, experience (list of jobs), "
            "projects, Certifications,Acheivements. "
            "Do not include any explanation or commentary."
        )

        # Define the request payload
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": resume_text}
            ],
            "temperature": 0.2,
            "max_tokens": 2000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }

        timeout = httpx.Timeout(30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Make the request to the API
            response = await client.post(AZURE_API_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            result = response.json()

            # Log the raw response
            logging.info(f"Response from OpenAI API: {result}")

            content = result["choices"][0]["message"]["content"].strip()

            # Remove backticks and format if returned inside a code block
            if content.startswith("```"):
                content = content.strip("`")
                content = content.replace("json", "", 1).strip()

            try:
                # Attempt to parse the content as JSON
                return json.loads(content)
            except json.JSONDecodeError:
                # Log and raise error if parsing fails
                logging.error(f"Invalid JSON returned by model:\n{content}")
                raise ValueError(f"Invalid JSON returned by model:\n{content}")

    except TimeoutException:
        logging.error("Request to Azure OpenAI timed out.")
        raise ValueError("The request timed out while contacting the Azure OpenAI API.")
    except Exception as e:
        logging.error(f"Error while parsing resume: {e}")
        raise
