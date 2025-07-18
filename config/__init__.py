import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Access the environment variables
username = os.getenv("MOODLE_USER")
psw = os.getenv("MOODLE_PASSWORD")
