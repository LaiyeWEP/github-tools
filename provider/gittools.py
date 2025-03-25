from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GiteaToolsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            # Validate Gitea credentials
            if 'gitea_access_token' not in credentials:
                raise ValueError('Gitea access token is required')
            if 'gitea_api_url' not in credentials:
                raise ValueError('Gitea API URL is required')
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
