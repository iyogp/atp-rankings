import os

from dotenv import load_dotenv

load_dotenv()

current = os.getenv("CURRENT")

print('current', current)