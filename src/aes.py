"""a custom AES implementation i can actually be sure fucking works with the client
in retrospect i think this is the first time i've not overdone something in this project and that is saying something"""

import base64
from hashlib import pbkdf2_hmac
from secrets import token_bytes
from Crypto.Cipher import AES


class AESGCM:
    """a class representing an AES-GCM cipher for encryption and decryption"""

    password: str

    def __init__(self, password: str) -> None:
        self.password = password

    def encrypt(self, plaintext: str) -> str:
        """encrypts a plaintext string using AES-GCM with the provided password

        :param plaintext: the string to encrypt
        :type plaintext: str
        :return: the encrypted bytes
        :rtype: bytes
        """
        salt = token_bytes(16)
        nonce = token_bytes(12)
        key = pbkdf2_hmac(
            hash_name="sha256",
            password=self.password.encode(),
            salt=salt,
            iterations=100000,
        )
        cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=nonce)
        ciphertext, mac = cipher.encrypt_and_digest(plaintext.encode())
        return base64.b64encode(salt + nonce + ciphertext + mac).decode()

    def decrypt(self, secretBox: str) -> str:
        """decrypts a secretBox string using AES-GCM with the provided password

        :param secretBox: the string to decrypt
        :type secretBox: str
        :return: the decrypted plaintext
        :rtype: str
        """
        decoded = base64.b64decode(secretBox)
        salt, nonce, ciphertext, mac = (
            decoded[:16],
            decoded[16:28],
            decoded[28:-16],
            decoded[-16:],
        )
        key = pbkdf2_hmac(
            hash_name="sha256",
            password=self.password.encode(),
            salt=salt,
            iterations=100000,
        )
        cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, mac)
        return plaintext.decode()
