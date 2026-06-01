import os
from dotenv import load_dotenv

load_dotenv()

print("COINGECKO_API_KEY =", os.getenv("COINGECKO_API_KEY"))
