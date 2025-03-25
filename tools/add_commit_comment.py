from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GiteaToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        commit_sha = tool_parameters.get("commit_sha")
        comment = tool_parameters.get("comment")
        
        if not commit_sha:
            yield self.create_text_message("Error: Commit SHA is required")
            return
            
        if not comment:
            yield self.create_text_message("Error: Comment content is required")
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
            
            # Gitea API endpoint for creating a comment on a commit
            url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/issues/{commit_sha}/comments"
            
            # 发送评论
            response = requests.post(url, headers=headers, json={"body": comment})
            response.raise_for_status()
            
            # 解析响应获取评论信息
            comment_data = response.json()
            result = {
                "id": comment_data["id"],
                "url": comment_data["html_url"],
                "created_at": comment_data["created_at"]
            }
            
            yield self.create_variable_message("comment", result)
            
        except Exception as e:
            yield self.create_text_message(f"Error adding comment to commit: {str(e)}")
