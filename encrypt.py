import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import key

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