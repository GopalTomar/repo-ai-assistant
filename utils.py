import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import git
import streamlit as st

class CodebaseManager:
    """Manages codebase operations like cloning and file handling"""
    
    def __init__(self):
        self.temp_dir = None
        self.repo_path = None
    
    @staticmethod
    def is_valid_github_url(url: str) -> bool:
        """Validate GitHub URL format"""
        return url.startswith(('https://github.com/', 'git@github.com:'))
    
    def clone_repository(self, repo_url: str) -> Optional[str]:
        """Clone repository and return local path"""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            self.repo_path = os.path.join(self.temp_dir, "repo")
            
            # Clone repository
            git.Repo.clone_from(repo_url, self.repo_path, depth=1)
            return self.repo_path
        except Exception as e:
            st.error(f"Failed to clone repository: {str(e)}")
            self.cleanup()
            return None
    
    def get_code_files(self, repo_path: str) -> List[Dict[str, str]]:
        """Get all relevant code files from the repository"""
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', 
            '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.scala',
            '.kt', '.swift', '.r', '.sql', '.md', '.txt', '.yml', '.yaml',
            '.json', '.xml', '.html', '.css', '.sh', '.dockerfile', '.vue'
        }
        
        ignore_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next',
            'target', 'bin', 'obj', '.idea', '.vscode', 'coverage',
            '.nyc_output', 'logs', 'temp', 'tmp'
        }
        
        ignore_files = {
            '.gitignore', '.env', '.env.local', '.DS_Store',
            'package-lock.json', 'yarn.lock', '.gitattributes',
            'LICENSE', 'license.txt'
        }
        
        files = []
        repo_path = Path(repo_path)
        
        for file_path in repo_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in code_extensions and
                file_path.name not in ignore_files and
                not any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs)):
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Skip very large files (>500KB)
                    if len(content) > 500000:
                        continue
                    
                    # Skip empty or very small files
                    if len(content.strip()) < 20:
                        continue
                    
                    relative_path = str(file_path.relative_to(repo_path))
                    files.append({
                        'path': relative_path,
                        'content': content,
                        'extension': file_path.suffix.lower()
                    })
                except Exception as e:
                    # Skip files that can't be read
                    continue
        
        return files
    
    def cleanup(self):
        """Clean up temporary directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None
            self.repo_path = None
    
    def get_repo_stats(self, files: List[Dict[str, str]]) -> Dict:
        """Get repository statistics"""
        extensions = {}
        total_lines = 0
        
        for file in files:
            ext = file['extension']
            line_count = len(file['content'].splitlines())
            
            if ext not in extensions:
                extensions[ext] = {'count': 0, 'lines': 0}
            
            extensions[ext]['count'] += 1
            extensions[ext]['lines'] += line_count
            total_lines += line_count
        
        return {
            'total_files': len(files),
            'total_lines': total_lines,
            'extensions': extensions
        }

def format_code_snippet(code: str, language: str = "python") -> str:
    """Format code snippet for display"""
    # Remove common indentation
    lines = code.split('\n')
    if lines:
        # Find minimum indentation (excluding empty lines)
        min_indent = float('inf')
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        if min_indent != float('inf') and min_indent > 0:
            lines = [line[min_indent:] if line.strip() else line for line in lines]
    
    return '\n'.join(lines)

def extract_repo_name(url: str) -> str:
    """Extract repository name from GitHub URL"""
    if url.endswith('.git'):
        url = url[:-4]
    return url.split('/')[-1]

def safe_markdown(text: str) -> str:
    """Safely render markdown, escaping potential problematic characters"""
    # Basic safety checks for markdown
    text = text.replace('```', '`\u200B`\u200B`')  # Zero-width space to break code blocks
    return text

def get_language_from_extension(extension: str) -> str:
    """Get programming language name from file extension"""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.scala': 'scala',
        '.kt': 'kotlin',
        '.swift': 'swift',
        '.r': 'r',
        '.sql': 'sql',
        '.md': 'markdown',
        '.html': 'html',
        '.css': 'css',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.vue': 'vue'
    }
    return extension_map.get(extension.lower(), 'text')