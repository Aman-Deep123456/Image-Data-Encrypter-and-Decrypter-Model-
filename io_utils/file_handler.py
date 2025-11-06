import os

def normalize_path(p: str) -> str:
    if not p:
        return p
    p = p.strip()
    if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
        p = p[1:-1]
    return os.path.expanduser(p)

def read_bytes(path: str) -> bytes:
    path = normalize_path(path)
    with open(path, 'rb') as f:
        return f.read()

def save_bytes(path: str, data: bytes):
    path = normalize_path(path)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)

def basename(path: str) -> str:
    return os.path.basename(path)
