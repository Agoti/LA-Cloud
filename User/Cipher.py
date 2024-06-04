
import hashlib

class MD5Cipher:

    @staticmethod
    def encrypt(message):
        return hashlib.md5(message.encode()).hexdigest()
