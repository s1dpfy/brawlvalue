import os
from dotenv import load_dotenv

load_dotenv()

BRAWL_API_KEY = os.getenv("BRAWL_API_KEY", "")
ROYALE_API_PROXY_URL = "https://bsproxy.royaleapi.dev/v1/players"