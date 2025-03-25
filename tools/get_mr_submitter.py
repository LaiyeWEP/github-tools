from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GiteaToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        mr_number = tool_parameters.get("mr_number")
        if not mr_number:
            yield self.create_text_message("Error: MR Number is required")
            return
            
        try:
            # 从self.runtime.credentials获取Gitea API配置
            gitea_token = self.runtime.credentials.get("gitea_access_token")
            gitea_api_url = self.runtime.credentials.get("gitea_api_url")
            
            # 构建API请求
            headers = {
                "Authorization": f"token {gitea_token}",
                "Accept": "application/json"
            }
            
            # 从参数中获取仓库所有者和仓库名
            owner = tool_parameters.get("repo_owner")
            repo = tool_parameters.get("repo_name")
            
            if not owner or not repo:
                yield self.create_text_message("Error: Repository owner and name are required")
                return
            
            url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/pulls/{mr_number}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 解析响应获取提交者信息
            pr_data = response.json()
            submitter = {
                "login": pr_data["user"]["login"],
                "name": pr_data["user"].get("name", ""),
                "email": pr_data["user"].get("email", ""),
            }
            
            yield self.create_variable_message("submitter", submitter)
            
        except Exception as e:
            yield self.create_text_message(f"Error fetching MR submitter: {str(e)}")
