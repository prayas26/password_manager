import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import key

# password_provided = "password"
# password = password_provided.encode()
# salt = b'salt_smartBuddy'
# kdf = PBKDF2HMAC(
#     algorithm=hashes.SHA256(),
#     length=32,
#     salt=salt,
#     iterations=100000,
#     backend=default_backend()
# )

getKey = key.passKey
fern = Fernet(getKey)

def encryptPassword(userPass):
    encrypted = fern.encrypt(userPass)
    return encrypted

def decryptPassword(hashPass):
    decrypted = fern.decrypt(hashPass)
    return decrypted