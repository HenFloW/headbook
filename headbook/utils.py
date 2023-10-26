import hashlib
import uuid

def hash_with_salt(password, salt):
    m = hashlib.sha256()
    m.update((salt + password).encode('utf-8'))
    return m.hexdigest()

def hash_password(password):
    salt = uuid.uuid4().hex
    return hash_with_salt(password, salt) + ':' + salt

def check_password(hashed, text):
    try:
      _hashed, salt = hashed.split(':')
      return _hashed == hash_with_salt(text, salt)
    except:
      return False