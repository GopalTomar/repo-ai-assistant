import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
import git
import streamlit as st
import subprocess

class CodebaseManager:
    """Manages codebase operations like cloning and file handling"""
    
    def __init__(self):
        self.temp_dir = None
        self.repo_path = None
    
    @staticmethod
    def is_valid_github_url(url: str) -> bool:
        """Validate GitHub URL format"""
        return url.startswith(('https://github.com/', 'git@github.com:'))
    
    @staticmethod
    def check_git_installation():
        """Check if git is properly installed"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            st.info(f"Git version: {result.stdout.strip()}")
            return True
        except Exception as e:
            st.error(f"Git check failed: {str(e)}")
            return False
    
    def clone_repository_subprocess(self, repo_url: str) -> Optional[str]:
        """Alternative clone method using subprocess (more reliable on cloud)"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="codebase_")
            self.repo_path = os.path.join(self.temp_dir, "repo")
            
            st.info(f"Cloning to: {self.repo_path}")
            
            # Use subprocess instead of GitPython for better compatibility
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, self.repo_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                st.success("Repository cloned successfully!")
                
                # Verify the directory exists
                if not os.path.exists(self.repo_path):
                    st.error(f"Repository path does not exist: {self.repo_path}")
                    return None
                
                # List directory contents
                contents = os.listdir(self.repo_path)
                st.info(f"Found {len(contents)} items in repository root")
                
                return self.repo_path
            else:
                st.error(f"Git clone failed: {result.stderr}")
                st.error("Possible reasons:")
                st.error("- Repository URL is incorrect")
                st.error("- Repository is private (requires authentication)")
                st.error("- Network connectivity issues")
                return None
                
        except subprocess.TimeoutExpired:
            st.error("Clone operation timed out (exceeded 5 minutes)")
            self.cleanup()
            return None
        except Exception as e:
            st.error(f"Clone failed: {str(e)}")
            st.error(f"Error type: {type(e).__name__}")
            self.cleanup()
            return None
    
    def clone_repository(self, repo_url: str) -> Optional[str]:
        """Clone repository and return local path - tries GitPython first, falls back to subprocess"""
        # First, check git installation
        if not self.check_git_installation():
            st.error("Git is not properly installed on the system")
            return None
        
        try:
            # Try GitPython method first
            self.temp_dir = tempfile.mkdtemp(prefix="codebase_")
            self.repo_path = os.path.join(self.temp_dir, "repo")
            
            st.info(f"Attempting to clone using GitPython...")
            
            try:
                repo = git.Repo.clone_from(
                    repo_url, 
                    self.repo_path, 
                    depth=1,
                    progress=None,
                    env={'GIT_TERMINAL_PROMPT': '0'}
                )
                st.success("Repository cloned successfully with GitPython!")
                
                # Verify
                if not os.path.exists(self.repo_path):
                    st.error(f"Repository path does not exist: {self.repo_path}")
                    return None
                
                contents = os.listdir(self.repo_path)
                st.info(f"Found {len(contents)} items in repository root")
                
                return self.repo_path
                
            except git.exc.GitCommandError as e:
                st.warning(f"GitPython failed: {str(e)}")
                st.info("Trying alternative method with subprocess...")
                
                # Clean up failed attempt
                self.cleanup()
                
                # Try subprocess method
                return self.clone_repository_subprocess(repo_url)
                
        except Exception as e:
            st.error(f"Failed to clone repository: {str(e)}")
            st.error(f"Error type: {type(e).__name__}")
            
            # Try subprocess as last resort
            st.info("Attempting final clone method...")
            self.cleanup()
            return self.clone_repository_subprocess(repo_url)
    
    def get_code_files(self, repo_path: str) -> List[Dict[str, str]]:
        """Get all relevant code files from the repository"""
        # ALL LOWERCASE for reliable comparison
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', 
            '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.scala',
            '.kt', '.swift', '.r', '.sql', '.md', '.txt', '.yml', '.yaml',
            '.json', '.xml', '.html', '.css', '.sh', '.dockerfile', '.vue',
            '.ipynb'  # Added Jupyter notebooks
        }
        
        # Directories to skip
        ignore_dirs = {
            '.git', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next',
            'target', 'bin', 'obj', '.idea', '.vscode', 'coverage',
            'saved_model', 'saved_model_01'
        }
        
        # Files to skip
        ignore_files = {
            '.gitignore', '.env', '.env.local', '.DS_Store',
            'package-lock.json', 'yarn.lock', '.gitattributes',
            'LICENSE', 'license.txt', 'LICENSE.md', '.gitkeep'
        }
        
        # Binary file extensions to skip
        binary_extensions = {
            '.h5', '.keras', '.npy', '.npz', '.pkl', '.pickle',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
            '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
            '.exe', '.dll', '.so', '.dylib', '.whl'
        }
        
        files = []
        repo_path = Path(repo_path)
        
        # Verify repo_path exists
        if not repo_path.exists():
            st.error(f"Repository path does not exist: {repo_path}")
            return []
        
        st.info(f"Scanning repository at: {repo_path}")
        
        # Walk through directory structure
        total_files_scanned = 0
        files_skipped = 0
        
        try:
            for file_path in repo_path.rglob('*'):
                total_files_scanned += 1
                
                # Skip if not a file
                if not file_path.is_file():
                    continue
                
                # Get file name and extension
                file_name = file_path.name
                file_extension = file_path.suffix.lower()
                
                # Skip if in ignore directory - check if ANY parent directory is in ignore list
                path_parts_lower = [p.lower() for p in file_path.parts]
                if any(ignore_dir.lower() in path_parts_lower for ignore_dir in ignore_dirs):
                    files_skipped += 1
                    continue
                
                # Skip if filename matches ignore list
                if file_name in ignore_files:
                    files_skipped += 1
                    continue
                
                # Skip binary files
                if file_extension in binary_extensions:
                    files_skipped += 1
                    continue
                
                # Check if this is a code file we want
                if file_extension not in code_extensions:
                    files_skipped += 1
                    continue
                
                # If we reach here, we found a code file!
                st.info(f"📄 Found code file: {file_name}")
                
                try:
                    # Read the file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check size
                    if len(content) > 500000:
                        st.warning(f"⚠️ Skipping {file_name}: too large ({len(content)} bytes)")
                        files_skipped += 1
                        continue
                    
                    # Check if file has meaningful content
                    if len(content.strip()) < 20:
                        st.warning(f"⚠️ Skipping {file_name}: too small ({len(content.strip())} chars)")
                        files_skipped += 1
                        continue
                    
                    # Add to our list!
                    relative_path = str(file_path.relative_to(repo_path))
                    files.append({
                        'path': relative_path,
                        'content': content,
                        'extension': file_extension
                    })
                    
                    st.success(f"✅ Added: {file_name}")
                    
                except Exception as e:
                    st.error(f"❌ Error reading {file_name}: {str(e)}")
                    files_skipped += 1
                    continue
            
            # Log results
            st.info(f"📊 Scan complete: {total_files_scanned} files scanned, "
                   f"{len(files)} code files found, {files_skipped} files skipped")
            
            # If no files found, provide detailed diagnostics
            if len(files) == 0:
                st.error("❌ No code files found!")
                st.error("**Debugging information:**")
                
                # List all files with their extensions
                try:
                    all_files = list(repo_path.rglob('*'))
                    py_files = [f for f in all_files if f.is_file() and f.suffix.lower() == '.py']
                    
                    st.info(f"**Total files in repo:** {len([f for f in all_files if f.is_file()])}")
                    st.info(f"**.py files found:** {len(py_files)}")
                    
                    if py_files:
                        st.error("**Python files detected but not added:**")
                        for pf in py_files[:10]:
                            st.error(f"  - {pf.name} at {pf.relative_to(repo_path)}")
                            
                            # Check why it was skipped
                            is_in_ignore_dir = any(ignore_dir.lower() in [p.lower() for p in pf.parts] 
                                                   for ignore_dir in ignore_dirs)
                            if is_in_ignore_dir:
                                st.error(f"    → Skipped: in ignored directory")
                            
                            try:
                                with open(pf, 'r') as f:
                                    content = f.read()
                                if len(content.strip()) < 20:
                                    st.error(f"    → Skipped: too small ({len(content.strip())} chars)")
                                elif len(content) > 500000:
                                    st.error(f"    → Skipped: too large ({len(content)} bytes)")
                                else:
                                    st.error(f"    → Should have been added! ({len(content)} chars)")
                            except Exception as e:
                                st.error(f"    → Error reading: {e}")
                
                except Exception as e:
                    st.error(f"Error during diagnostics: {e}")
        
        except Exception as e:
            st.error(f"Error scanning repository: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
        
        return files
    
    def cleanup(self):
        """Clean up temporary directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                st.info("Cleaned up temporary files")
            except Exception as e:
                st.warning(f"Cleanup warning: {str(e)}")
            finally:
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
    lines = code.split('\n')
    if lines:
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
    text = text.replace('```', '`\u200B`\u200B`')
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
