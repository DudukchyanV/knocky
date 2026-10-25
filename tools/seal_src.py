"""Encrypted copy of the working sources (design parts, build script, local tests, doc sources).
The repo is public, so the sources are stored only encrypted (AES-GCM, key wrapped by each password with PBKDF2-SHA256),
same passwords as the site (index.html).

Pack:   python3 tools/seal_src.py pack  SRC_DIR  src/knocky-src.enc  PASSWORD1 PASSWORD2
Unpack: python3 tools/seal_src.py unpack src/knocky-src.enc  OUT_DIR  PASSWORD
"""
import base64, io, json, os, sys, tarfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000
b64, ub64 = (lambda b: base64.b64encode(b).decode()), base64.b64decode
kdf = lambda pw, s: PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=s, iterations=ITER).derive(pw.encode())

def pack(src, out, pws):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(src, arcname=".")
    K, iv = os.urandom(32), os.urandom(12)
    wraps = []
    for pw in pws:
        s, wi = os.urandom(16), os.urandom(12)
        wraps.append({"s": b64(s), "i": b64(wi), "w": b64(AESGCM(kdf(pw, s)).encrypt(wi, K, None))})
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump({"i": b64(iv), "c": b64(AESGCM(K).encrypt(iv, buf.getvalue(), None)), "n": ITER, "k": wraps}, open(out, "w"))
    print("sealed", out, os.path.getsize(out) // 1024, "KB")

def unpack(src, out, pw):
    d = json.load(open(src))
    for w in d["k"]:
        try:
            K = AESGCM(kdf(pw, ub64(w["s"]))).decrypt(ub64(w["i"]), ub64(w["w"]), None); break
        except Exception:
            continue
    else:
        sys.exit("wrong password")
    data = AESGCM(K).decrypt(ub64(d["i"]), ub64(d["c"]), None)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
        t.extractall(out, filter="data")
    print("unpacked to", out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    pack(sys.argv[2], sys.argv[3], sys.argv[4:]) if cmd == "pack" else unpack(sys.argv[2], sys.argv[3], sys.argv[4])
