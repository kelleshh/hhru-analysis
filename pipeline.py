import os
import time
import random
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Libs for parsing
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Set configs

BASE_URL: str = 'https://hh.ru/search/vacancy'

AREA_URL: str = '?area='
AREA: int = 1 # Москва

ROLE_URL: str = '&professional_role='
ROLE_START: int = 1
ROLE_END: int = 174

PER_PAGE = 50

OUT_DIR = Path("./data/raw_html")
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = (5, 20)  # (connect, read)
DELAY_RANGE_SEC = (1.5, 3.5)  # случайная задержка между запросами
LANG_COOKIE = "hhuid=anonymous;"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}

