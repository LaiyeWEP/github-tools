from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GiteaToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        mr_number = tool_parameters.get("mr_number")
        file_path = tool_parameters.get("file_path")  # 可选参数，用于获取特定文件的diff

        if not mr_number:
            yield self.create_text_message("Error: MR number is required")
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

            headers = {
                "Authorization": f"token {gitea_token}",
                "Accept": "text/plain"
            }

            if file_path:
                # 如果指定了文件路径，获取完整diff并解析
                url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/pulls/{mr_number}.diff"
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                full_diff = response.text
                
                # 解析diff内容，查找指定文件的diff
                diff_sections = full_diff.split('diff --git ')
                diff_content = None
                
                for section in diff_sections:
                    if section.strip() and file_path in section.split('\n')[0]:
                        diff_content = 'diff --git ' + section
                        break
                
                if diff_content is None:
                    yield self.create_text_message(f"Error: File '{file_path}' not found in the merge request")
                    return
            else:
                # 如果没有指定文件路径，获取完整的diff
                url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/pulls/{mr_number}.diff"
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                diff_content = response.text
            
            yield self.create_variable_message("diff_content", diff_content)
            
        except Exception as e:
            yield self.create_text_message(f"Error fetching merge request diff: {str(e)}")
