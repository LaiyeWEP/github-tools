from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GiteaToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        commit_sha = tool_parameters.get("commit_sha")
        file_type_blacklist = tool_parameters.get("file_type_blacklist", "")  # 可选参数，用于排除文件类型
        
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
            
            url = f"{gitea_api_url}/api/v1/repos/{owner}/{repo}/git/commits/{commit_sha}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 解析响应获取差异文件列表
            commit_data = response.json()
            files_data = commit_data.get("files", [])
            
            # 解析黑名单
            blacklist_extensions = []
            if file_type_blacklist:
                blacklist_extensions = [ext.strip() for ext in file_type_blacklist.split(",")]
            
            # 提取修改的文件名并去重，排除黑名单中的文件类型
            unique_files = set()
            for file_info in files_data:
                filename = file_info.get("filename")
                if filename:
                    # 检查文件是否在黑名单中
                    should_exclude = False
                    for ext in blacklist_extensions:
                        if filename.endswith(f".{ext}"):
                            should_exclude = True
                            break
                    
                    # 如果文件不在黑名单中，则添加到结果中
                    if not should_exclude:
                        unique_files.add(filename)
            
            # 将集合转换为排序列表
            file_list = sorted(list(unique_files))
            
            yield self.create_variable_message("diff_files", file_list)
            
        except Exception as e:
            yield self.create_text_message(f"Error fetching commit diff file list: {str(e)}")
