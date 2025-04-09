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
            if 'feishu_app_id' not in credentials:
                raise ValueError('feishu_app_id is required')
            if 'feishu_app_secret' not in credentials:
                raise ValueError('Gfeishu_app_secret is required')
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
