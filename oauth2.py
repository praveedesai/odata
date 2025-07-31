from fastapi.security.oauth2 import OAuth2, OAuthFlowsModel
from typing import Optional
from dotenv import load_dotenv
import os

# OAuth2 configuration
OAUTH2_TOKEN_URL = "https://coe-asset-b9jxgzf0.authentication.eu10.hana.ondemand.com/oauth/token"

class OAuth2ClientCredentials(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
    ):
        flows = OAuthFlowsModel(
            clientCredentials={"tokenUrl": tokenUrl}
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            auto_error=True
        )

        self.SAP_PROVIDER_URL = self._get_env_var("SAP_PROVIDER_URL")

    def _get_env_var(self, key, default=None):
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value    

# Create OAuth2 scheme instance
oauth2_scheme = OAuth2ClientCredentials(
    tokenUrl=OAUTH2_TOKEN_URL,
) 