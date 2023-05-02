import re
import argon2 as ar
from pymongo import MongoClient


def credentials(regex, name):
    param = ""
    while not re.fullmatch(regex, param):
        param = input(f"Enter {name} : ")
    return param


mongoClient = MongoClient("localhost", 27017)

db = mongoClient["userdata"]
collection = db["admin_mail"]

id_regex = r"^[a-zA-Z]{3}[0-9]{11}$"
pass_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
mail_regex = r"^[a-zA-Z0-9.]{1,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,8}[a-zA-Z]{2,63}$"

uid = credentials(id_regex, "UID")
password = credentials(pass_regex, "Password")
mail = credentials(mail_regex, "Mail")

mails = {"mail": "%s" % (mail)}
if not collection.count_documents(mails):
    collection.insert_one(mails)

collection = db["admin"]

ph = ar.PasswordHasher(hash_len=64)
uid = ph.hash(uid)

ph = ar.PasswordHasher(hash_len=64)
password = ph.hash(password)

print(uid)
print(password)
creds = {"id": "%s" % (uid), "pass": "%s" % (password)}

if collection.insert_one(creds):
    print("Admin added")
