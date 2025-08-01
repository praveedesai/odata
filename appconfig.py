import os
import json
import base64
import requests
import datetime
import logging
from os.path import join, dirname, exists
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

config_instance = None

class AppConfig:
    def __init__(self):
        # Load environment variables from .env file if it exists
        dotenv_path = join(dirname(__file__),  '.env')
        if exists(dotenv_path):
            print('Loading the local env file found at :', dotenv_path)
            load_dotenv(dotenv_path=dotenv_path)
        else:
            print(f"Warning: .env file not found at {dotenv_path}")

        self.LOCAL_ENV = os.getenv("ENV", "PROD").upper() == "LOCAL"
        logger.info(f"[AppConfig] ENV mode: {'LOCAL' if self.LOCAL_ENV else 'PROD'}")
        self.destination_token_cache = {"token": None, "expires_at": None}
        self.connectivity_token_cache = {"token": None, "expires_at": None}

        if self.LOCAL_ENV:
            logger.info("[AppConfig] Loading local environment variables...")
            self._load_local_env()
        else:
            logger.info("[AppConfig] Loading production environment variables...")
            self._load_production_env()
        self.app = self._create_fastapi_app()   
  
    

    def _create_fastapi_app(self) -> FastAPI:
        app = FastAPI(
            title="Data Stories API",
            description="Enterprise-grade API for generating data stories",
            version="1.0.0"
        )
        
        # Configure CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Configure OAuth UI
        app.swagger_ui_init_oauth = {
            "usePkceWithAuthorizationCodeGrant": False,
        }      
         
        return app

    def _load_local_env(self):
        self.ODATA_USERNAME = self._get_env_var("ODATA_USERNAME")
        self.ODATA_PASSWORD = self._get_env_var("ODATA_PASSWORD")
        self.ODATA_ENDPOINT = self._get_env_var("ODATA_ENDPOINT")       
        self.PROXIES = None
        self.ODATA_HEADERS = None
        logger.info(f"[AppConfig] Local ODATA config: USERNAME={self.ODATA_USERNAME}, ENDPOINT={self.ODATA_ENDPOINT}")
        

    def _load_production_env(self):
        self.LOCAL_ENV = os.getenv("ENV", "PROD").upper() == "LOCAL"
        # self._set_destination_service()     
           
    
    # def _set_destination_service(self):        
    #     self.destination_name = "DOUS4HANA"
    #     logger.info("[AppConfig] Fetching destination and connectivity tokens...")
    #     token = self.get_destination_token()
    #     conn_token = self.get_connectivity_token()
    #     logger.info(f"[AppConfig] Destination token: {token[:10]}... (truncated)")
    #     logger.info(f"[AppConfig] Connectivity token: {conn_token[:10]}... (truncated)")
    #     headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    #     destination_url = f"{os.getenv('DESTINATION_SERVICE_URL')}/destination-configuration/v1/destinations/{self.destination_name}"
    #     logger.info(f"[AppConfig] Requesting destination details from: {destination_url}")
    #     destination_details = requests.get(destination_url, headers=headers)

    #     if destination_details.status_code != 200:
    #         logger.error(f"[AppConfig] Destination details error: {destination_details.text}")
    #         raise ValueError(f"Failed to retrieve destination: Status {destination_details.status_code} - {destination_details.text}")
        
    #     destination_response = destination_details.json()
    #     logger.info(f"[AppConfig] Retrieved destination config keys: {list(destination_response['destinationConfiguration'].keys())}")
    #     self.ODATA_USERNAME = destination_response['destinationConfiguration'].get('User')
    #     self.ODATA_PASSWORD = destination_response['destinationConfiguration'].get('Password')
    #     self.ODATA_ENDPOINT = f"{destination_response['destinationConfiguration']['URL']}"          
    #     conn_proxy_host = os.getenv('CONNECTIVITY_SERVICE_ONPREMISE_PROXY_HOST')
    #     conn_proxy_port = int(os.getenv('CONNECTIVITY_SERVICE_ONPREMISE_PROXY_PORT'))
    #     self.PROXIES = {
    #         "http": f"http://{conn_proxy_host}:{conn_proxy_port}",
    #         "https": f"https://{conn_proxy_host}:{conn_proxy_port}"
    #     }
    #     self.ODATA_HEADERS = {  
    #             "Content-Type": "application/xml",
    #             "Proxy-Authorization": f"Bearer {conn_token}",
    #             "SAP-Connectivity-SCC-Location_ID": "DOU"
    #         }

    # def get_destination_token(self):
    #     if not self.destination_token_cache["token"] or self._is_token_expired(self.destination_token_cache):
    #         self._refresh_destination_token()
    #     return self.destination_token_cache["token"]

    # def get_connectivity_token(self):
    #     if not self.connectivity_token_cache["token"] or self._is_token_expired(self.connectivity_token_cache):
    #         self._refresh_connectivity_token()
    #     return self.connectivity_token_cache["token"]

    # def _is_token_expired(self, token_cache):
    #     return token_cache["expires_at"] is None or datetime.datetime.now().timestamp() >= token_cache["expires_at"]

    # def _refresh_destination_token(self):
    #     # Read all required values directly from environment variables
    #     destination_url = os.getenv("DESTINATION_SERVICE_URL")
    #     destination_client_id = os.getenv("DESTINATION_SERVICE_CLIENT_ID")
    #     destination_client_secret = os.getenv("DESTINATION_SERVICE_CLIENT_SECRET")
    #     logger.info(f"[AppConfig] Refreshing destination token for URL: {destination_url}")
    #     if not (destination_url and destination_client_id and destination_client_secret):
    #         logger.error("[AppConfig] Missing destination token env vars!")
    #         raise ValueError("Missing DESTINATION_SERVICE_URL, DESTINATION_SERVICE_CLIENT_ID, or DESTINATION_SERVICE_CLIENT_SECRET in environment variables.")

    #     auth_header = self._get_basic_auth_header_env(destination_client_id, destination_client_secret)
    #     form_data = self._get_token_form_data_env(destination_client_id, destination_client_secret)
    #     logger.info(f"[AppConfig] Destination token request: {form_data}")
    #     logger.info(f"[AppConfig] Destination token auth header: {auth_header}")
    #     response = requests.post(f"{destination_url}", data=form_data, headers=auth_header)
    #     logger.info(f"[AppConfig] Destination token response status: {response.status_code}")
    #     if response.status_code != 200:
    #         logger.error(f"[AppConfig] Destination token error: {response.text}")
    #         raise ValueError(f"Failed to retrieve destination token: Status {response.status_code} - {response.text}")
    #     try:
    #         json_response = response.json()
    #         logger.info(f"[AppConfig] Destination token response: {json_response}")
    #         self.destination_token_cache["token"] = json_response.get('access_token')
    #     except Exception as ex:
    #         logger.error(f"[AppConfig] Failed to decode JSON response: {response.text}")
    #         raise
    #     logger.info(f"[AppConfig] Destination token: {self.destination_token_cache['token'][:10]}... (truncated)")
    #     self.destination_token_cache["expires_at"] = datetime.datetime.now().timestamp() + 2 * 3600  # 2 hours

    # def _get_basic_auth_header_env(self, clientid, clientsecret):
    #     auth = f"{clientid}:{clientsecret}"
    #     return {'Authorization': 'Basic ' + base64.b64encode(auth.encode()).decode(), 'Content-Type': 'application/x-www-form-urlencoded'}

    # def _get_token_form_data_env(self, clientid, clientsecret):
    #     return {
    #         'client_id': clientid,
    #         'client_secret': clientsecret,
    #         'grant_type': 'client_credentials'
    #     }


    # def _refresh_connectivity_token(self):
    #     connectivity_url = os.getenv("CONNECTIVITY_SERVICE_URL")
    #     connectivity_client_id = os.getenv("CONNECTIVITY_SERVICE_CLIENT_ID")
    #     connectivity_client_secret = os.getenv("CONNECTIVITY_SERVICE_CLIENT_SECRET")
    #     logger.info(f"[AppConfig] Refreshing connectivity token for URL: {connectivity_url}")
    #     if not (connectivity_url and connectivity_client_id and connectivity_client_secret):
    #         logger.error("[AppConfig] Missing connectivity token env vars!")
    #         raise ValueError("Missing CONNECTIVITY_SERVICE_URL, CONNECTIVITY_SERVICE_CLIENT_ID, or CONNECTIVITY_SERVICE_CLIENT_SECRET in environment variables.")

    #     auth_header = self._get_basic_auth_header_env(connectivity_client_id, connectivity_client_secret)
    #     form_data = self._get_token_form_data_env(connectivity_client_id, connectivity_client_secret)
    #     response = requests.post(f"{connectivity_url}/oauth/token", data=form_data, headers=auth_header)
    #     logger.info(f"[AppConfig] Connectivity token response status: {response.status_code}")
    #     if response.status_code != 200:
    #         logger.error(f"[AppConfig] Connectivity token error: {response.text}")
    #         raise ValueError(f"Failed to retrieve connectivity token: Status {response.status_code} - {response.text}")

    #     try:
    #         json_response = response.json()
    #         logger.info(f"[AppConfig] Connectivity token response: {json_response}")
    #         self.connectivity_token_cache["token"] = json_response.get('access_token')
    #         logger.info(f"[AppConfig] Connectivity token: {self.connectivity_token_cache['token'][:10]}... (truncated)")
    #     except Exception as ex:
    #         logger.error(f"[AppConfig] Failed to decode JSON response: {response.text}")
    #         raise
    #     self.connectivity_token_cache["expires_at"] = datetime.datetime.now().timestamp() + 2 * 3600  # 2 hours


    # def _get_env_var(self, key, default=None):
    #     value = os.getenv(key, default)
    #     if value is None:
    #         raise ValueError(f"Missing required environment variable: {key}")
    #     return value

    # def _print_env(self):
    #     for key, value in os.environ.items():
    #         print(f"{key}={value}")

    # def to_json(self):
    #     return json.dumps(self.__dict__, indent=4)

def get_config_instance():
    global config_instance
    if config_instance is None:
        config_instance = AppConfig()
    return config_instance

if __name__ == "__main__":
    app = get_config_instance()
    print(f"If LOCAL? : {app.LOCAL_ENV}")