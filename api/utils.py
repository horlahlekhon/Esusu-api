import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

from api.settings import (DOMAIN, MAILJET_API_KEY, MAILJET_API_SECRET,
                          REGISTERED_MAIL, SITE_ADMIN, SECRET_KEY)
from mailjet_rest import Client
from rest_framework import serializers



class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        return self._choices[obj]

def send_mail(subject, user, text_heading, payload):
    mail_client = Client(
        auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    data = data = {
        'Messages': [
            {
                "From": {
                    "Email": REGISTERED_MAIL,
                    "Name": SITE_ADMIN
                },
                "To": [
                    {
                        "Email": user.email,
                        "Name": user.username
                    }
                ],
                "Subject": subject,
                "TextPart": text_heading,
                "HTMLPart": payload
            }
        ]
    }
    response = mail_client.send.create(data=data)
    return response


BLOCK_SIZE=16
def trans(key):
     return  hashlib.md5(key.encode()).digest()

def encrypt(message, passphrase):
    passphrase = trans(passphrase)
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return base64.b64encode(IV + aes.encrypt(message))

def decrypt(encrypted, passphrase):
    passphrase = trans(passphrase)
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return aes.decrypt(encrypted[BLOCK_SIZE:])


import json
import datetime



class DateTimeEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)