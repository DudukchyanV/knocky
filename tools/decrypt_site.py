"""Recover the site source (konvert.html) from the encrypted index.html.
Usage: python3 tools/decrypt_site.py index.html OUT.html PASSWORD
The source is never stored unencrypted in this public repo; index.html is the only copy."""
import sys, re, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
src, out, pw = sys.argv[1:4]
b = base64.b64decode
P = json.loads(re.search(r'const P=(\{.*?\});', open(src).read()).group(1))
for w in P['k']:
    k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b(w['s']), iterations=P['n']).derive(pw.encode())
    try:
        K = AESGCM(k).decrypt(b(w['i']), b(w['w']), None); break
    except Exception:
        K = None
if K is None: sys.exit('wrong password')
open(out, 'w').write(AESGCM(K).decrypt(b(P['i']), b(P['c']), None).decode())
print('ok ->', out)
