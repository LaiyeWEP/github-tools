from collections.abc import Generator
from typing import Any
import requests
import base64

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GiteaToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        commit_sha = tool_parameters.get("commit_sha")
        file_path = tool_parameters.get("file_path")
        
        if not commit_sha:
            yield self.create_text_message("Error: Commit SHA is required")
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
            
            # 获取commit信息
            commit_url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/git/commits/{commit_sha}"
            commit_response = requests.get(commit_url, headers=headers)
            commit_response.raise_for_status()
            
            commit_data = commit_response.json()
            
            # 如果提供了特定文件路径，则只获取该文件的内容
            if file_path:
                content = self._get_file_content(gitea_api_url, owner, repo, file_path, commit_sha, headers)
                if content:
                    yield self.create_variable_message("file_content", {
                        "file_path": file_path,
                        "content": content
                    })
                else:
                    yield self.create_text_message(f"Error: Could not retrieve content for {file_path}")
            # 如果没有提供文件路径，则获取commit中所有文件的内容
            else:
                files_data = commit_data.get("files", [])
                
                # 提取文件名
                file_paths = [file_info.get("filename") for file_info in files_data if file_info.get("filename")]
                
                # 获取每个文件的内容
                all_files_content = {}
                for path in file_paths:
                    content = self._get_file_content(gitea_api_url, owner, repo, path, commit_sha, headers)
                    if content:
                        all_files_content[path] = content
                
                yield self.create_variable_message("file_content", all_files_content)
            
        except Exception as e:
            yield self.create_text_message(f"Error fetching file content: {str(e)}")
    
    def _get_file_content(self, api_url, owner, repo, file_path, ref, headers):
        """获取指定文件的内容"""
        try:
            content_url = f"{api_url}/api/v1/repos/{owner}/{repo}/contents/{file_path}?ref={ref}"
            content_response = requests.get(content_url, headers=headers)
            content_response.raise_for_status()
            
            file_data = content_response.json()
            
            # Gitea API 也返回 Base64 编码的内容
            if "content" in file_data:
                # 解码Base64内容
                return base64.b64decode(file_data["content"]).decode("utf-8")
            
            return None
        except Exception:
            # 如果获取文件内容失败，返回None
            return None
