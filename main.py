from fastapi import FastAPI, HTTPException
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

EXTERNAL_API_URL = "https://inawconetput1.atrapa.deloitte.com:44300/sap/opu/odata4/sap/zs3_acdoca/srvd_a2x/sap/zs_acdoca/0001/ZC_ACDOCA"  # Replace with your API URL

@app.get("/fetch-ten")
def fetch_ten_rows():
    try:
        response = requests.get(EXTERNAL_API_URL, verify=False)
        response.raise_for_status()
        data = response.json()
        # Extract the first 10 items from the "value" array if present
        if isinstance(data, dict) and "value" in data and isinstance(data["value"], list):
            return data["value"][:10]
        return data  # fallback: return the whole response if "value" is missing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))