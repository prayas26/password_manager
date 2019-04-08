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

class Cipher(object):
    def __init__(self):
        self.getKey = key.passKey

    def encryptPassword(self, userPass):
        fern = Fernet(self.getKey)
        userPass = userPass.encode()
        encrypted = fern.encrypt(userPass)
        return encrypted

    def decryptPassword(self, hashPass):
        fern = Fernet(self.getKey)
        hashPass = hashPass.encode()
        decrypted = fern.decrypt(hashPass)
        return decrypted