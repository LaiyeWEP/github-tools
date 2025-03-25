from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GiteaToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        commit_sha = tool_parameters.get("commit_sha")
        file_path = tool_parameters.get("file_path")  # 可选参数，用于获取特定文件的diff

        if not commit_sha:
            yield self.create_text_message("Error: Commit SHA is required")
            return
            
        try:
            # 从self.runtime.credentials获取Gitea API配置
            gitea_token = self.runtime.credentials.get("gitea_access_token")
            gitea_api_url = self.runtime.credentials.get("gitea_api_url")
            
            # 从参数中获取仓库所有者和仓库名
            owner = tool_parameters.get("repo_owner")
            repo = tool_parameters.get("repo_name")
            
            if not owner or not repo:
                yield self.create_text_message("Error: Repository owner and name are required")
                return

            if file_path:
                # 如果指定了文件路径，获取特定文件的diff
                headers = {
                    "Authorization": f"token {gitea_token}",
                    "Accept": "application/json"
                }
                url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/git/commits/{commit_sha}.diff"
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                commit_data = response.json()
                files_data = commit_data.get("files", [])
                diff_content = None
                
                # 在文件列表中查找指定文件
                for file_info in files_data:
                    if file_info.get("filename") == file_path:
                        diff_content = file_info.get("patch", "")
                        break
                
                if diff_content is None:
                    yield self.create_text_message(f"Error: File '{file_path}' not found in the commit")
                    return
            else:
                # 如果没有指定文件路径，获取完整的diff
                headers = {
                    "Authorization": f"token {gitea_token}",
                    "Accept": "text/plain"
                }
                url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/git/commits/{commit_sha}.diff"
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                diff_content = response.text
            
            yield self.create_variable_message("diff_content", diff_content)
            
        except Exception as e:
            yield self.create_text_message(f"Error fetching commit diff: {str(e)}")
