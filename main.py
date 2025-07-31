import logging
from fastapi import FastAPI, HTTPException
import requests
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

from appconfig import get_config_instance

app = FastAPI()

config = get_config_instance()
logger.info("[main.py] Loaded config instance.")
logger.info(f"[main.py] ODATA_USERNAME: {config.ODATA_USERNAME}")
logger.info(f"[main.py] ODATA_ENDPOINT: {config.ODATA_ENDPOINT}")
logger.info(f"[main.py] ODATA_HEADERS: {config.ODATA_HEADERS}")
logger.info(f"[main.py] ODATA_PROXIES: {config.PROXIES}")

full_url = "http://inawconetput1.atrapa.deloitte.com:8000/sap/opu/odata4/sap/zsb_po_grn_sb4/srvd_a2x/sap/zsd_po_grn_det/0001/ZC_GRN_PO_DET?"

ODATA_USERNAME = config.ODATA_USERNAME
ODATA_PASSWORD = config.ODATA_PASSWORD
ODATA_HEADERS = config.ODATA_HEADERS
ODATA_PROXIES = config.PROXIES

@app.get("/health")
def health_check():
    logger.info("[main.py] /health endpoint called.")
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"[main.py] Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fetch-ten")
def fetch_ten_rows():
    try:
        logger.info(f"full_url: {full_url}")
        logger.info(f"ODATA_PROXIES: {ODATA_PROXIES}")
        logger.info(f"ODATA_HEADERS: {ODATA_HEADERS}")
        logger.info(f"ODATA_USERNAME: {ODATA_USERNAME}")
        logger.info(f"ODATA_PASSWORD: {ODATA_PASSWORD}")
        if ODATA_PROXIES is None:
             logger.info("ODATA_PROXIES is None")
             response = requests.get(url=full_url, auth=HTTPBasicAuth(str(ODATA_USERNAME), str(ODATA_PASSWORD)))
        else:           
             logger.info("ODATA_PROXIES is not None")
             response = requests.get(url=full_url,
                            proxies=ODATA_PROXIES,
                            headers=ODATA_HEADERS, 
                            auth=HTTPBasicAuth(str(ODATA_USERNAME), str(ODATA_PASSWORD))) 
        response.raise_for_status()
        data = response.json()
        # Extract the first 10 items from the "value" array if present
        if isinstance(data, dict) and "value" in data and isinstance(data["value"], list):
            return data["value"][:10]
        return data  # fallback: return the whole response if "value" is missing
    except Exception as e:
        logger.error(f"[main.py] fetch-ten error: {e}")
        raise HTTPException(status_code=500, detail=str(e))