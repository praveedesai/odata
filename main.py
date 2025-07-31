from fastapi import FastAPI, HTTPException
import requests
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from appconfig import get_config_instance

app = FastAPI()

full_url = "https://inawconetput1.atrapa.deloitte.com:44300/sap/opu/odata4/sap/zs3_acdoca/srvd_a2x/sap/zs_acdoca/0001/ZC_ACDOCA"  # Replace with your API URL


config = get_config_instance()
ODATA_USERNAME = config.ODATA_USERNAME
ODATA_PASSWORD=  config.ODATA_PASSWORD
ODATA_HEADERS =  config.ODATA_HEADERS if not config.LOCAL_ENV else None
ODATA_PROXIES =  config.PROXIES if not config.LOCAL_ENV else None
ODATA_ENDPOINT = config.ODATA_ENDPOINT

@app.get("/fetch-ten")
def fetch_ten_rows():
    try:
        print("full_url", full_url)
        print("ODATA_PROXIES", ODATA_PROXIES)
        print("ODATA_HEADERS", ODATA_HEADERS)
        print("ODATA_USERNAME", ODATA_USERNAME)
        print("ODATA_PASSWORD", ODATA_PASSWORD)
        if ODATA_PROXIES is None:
             print("ODATA_PROXIES is None")
             response = requests.get(url=full_url, auth=HTTPBasicAuth(str(ODATA_USERNAME), str(ODATA_PASSWORD)))
        else:           
             print("ODATA_PROXIES is not None")
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
        raise HTTPException(status_code=500, detail=str(e))