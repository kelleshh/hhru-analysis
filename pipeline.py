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

OUT_DIR = Path("C:/Users/mixso/OneDrive/Desktop/hhru-analysis/data/raw_html") 
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



# HTTP-session with retries

def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections= 10, pool_maxsize=10)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session



# Parsing dummy

def parse_dummy(html: str) -> List[Dict[str, Any]]:
    """
    TOD0: сюда позже надо добавить разбор вакансий из сохраненного HTML.
    Пример целевых полей:
      - vacancy_id, name, employer, area, published_at, salary, url
    На данном шаге мы ничего не парсим — только сохраняем сырой HTML.
    """
    return []



# Page fetching

def fetch_page(session: requests.Session, page: int) -> Optional[str]:
    params = { # type: ignore
        'area': AREA,
        'page': page-1,
        "hhtmFrom": "vacancy_search_list",
        "items_on_page": PER_PAGE,
        # можно еще добавть фильтры другие
    }
    resp = session.get(
        BASE_URL,
        params=params, # type: ignore
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )

    if resp.status_code == 200 and 'data-qa' in resp.text:
        return resp.text
    else:
        logging.warning(f'Non-OK or suspicious response: {resp.status_code} (len={len(resp.text)})')
        return None
    

    
# Main process

def main():
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s %(levelname)s %(message)s")
    session: requests.Session = make_session()

    logging.info(f'Start fetching roles {ROLE_START}-{ROLE_END} (area={AREA})')

    for i in range(ROLE_START, ROLE_END + 1):
        try:
            html: str | None = fetch_page(session, i)
            if not html:
                logging.warning(f'Skip page {i}: empty or blocked')
            else:
                out_path: Path = OUT_DIR / f'hh_search_page_{i:03d}.html'
                out_path.write_text(html, encoding='utf-8')
                logging.info(f'Saved page {i} -> {out_path} ({len(html)/1024:.1f} KB)')
                # заглушка вызова парсера
                # records = parse_dummy(html)
                # TOD0: сохранить извлечённые записи в CSV/DB
        except Exception as e:
            logging.exception(f'Error on page {i}: {e}')

        # Pause between queries - human imitation
        time.sleep(random.uniform(*DELAY_RANGE_SEC))
    
    logging.info('End.')
    

if __name__ == '__main__':
    main()