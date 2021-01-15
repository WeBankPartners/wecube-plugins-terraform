# _*_ coding:utf-8 _*_

import os
import base64
import binascii
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


def b64decode_key(key):
    new_key = key
    max_padding = 3
    while max_padding > 0:
        try:
            return base64.b64decode(new_key)
        except (binascii.Error, TypeError) as e:
            new_key += '='
            max_padding -= 1
            if max_padding <= 0:
                raise e


def decrypt_rsa(key, text):
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    random_generator = Random.new().read
    res = cipher.decrypt(b64decode_key(text), random_generator)
    return res.decode('utf-8')


def decode_passwd(RSA_FILE, password):
    if password.startswith("RSA@"):
        if not os.path.exists(RSA_FILE):
            raise ValueError("rsa file not exists, please mount")
        with open(RSA_FILE) as file:
            return decrypt_rsa(file, text=password[len("RSA@"):])
    else:
        return password

