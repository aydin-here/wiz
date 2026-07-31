import hashlib
import uuid
import secrets
import base64


class CryptoModule:

    def __init__(self):
        self.functions = {
            "md5": self.md5,
            "sha1": self.sha1,
            "sha224": self.sha224,
            "sha256": self.sha256,
            "sha384": self.sha384,
            "sha512": self.sha512,

            "uuid": self.uuid,

            "random_bytes": self.random_bytes,

            "base64_encode": self.base64_encode,
            "base64_decode": self.base64_decode,

            "hex_encode": self.hex_encode,
            "hex_decode": self.hex_decode,
        }

    def md5(self, text):
        return hashlib.md5(str(text).encode()).hexdigest()

    def sha1(self, text):
        return hashlib.sha1(str(text).encode()).hexdigest()

    def sha224(self, text):
        return hashlib.sha224(str(text).encode()).hexdigest()

    def sha256(self, text):
        return hashlib.sha256(str(text).encode()).hexdigest()

    def sha384(self, text):
        return hashlib.sha384(str(text).encode()).hexdigest()

    def sha512(self, text):
        return hashlib.sha512(str(text).encode()).hexdigest()

    def uuid(self):
        return str(uuid.uuid4())

    def random_bytes(self, length):
        return secrets.token_bytes(length)

    def base64_encode(self, text):
        return base64.b64encode(str(text).encode()).decode()

    def base64_decode(self, text):
        return base64.b64decode(text).decode()

    def hex_encode(self, text):
        return str(text).encode().hex()

    def hex_decode(self, text):
        return bytes.fromhex(text).decode()