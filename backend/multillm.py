from groq import Groq
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()


class groqconnect:
    def groqinference(imagelist, prompt):

        logging.info("Groq inference being run . ..")

        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": imagelist[0]}},
                        {"type": "image_url", "image_url": {"url": imagelist[1]}},
                        {"type": "image_url", "image_url": {"url": imagelist[2]}},
                        {"type": "image_url", "image_url": {"url": imagelist[3]}},
                        {"type": "image_url", "image_url": {"url": imagelist[4]}},
                    ],
                },
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            stream=False,
            response_format={"type": "json_object"},
            max_completion_tokens=2048,
        )
        try:
            groq_response = chat_completion.choices[0].message.content
        except Exception as e:
            logging.error(f"Error during groq inference: {str(e)}")
        # print("groq response : ", groq_response)
        return groq_response
