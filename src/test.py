import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from pprint import pprint

from config import config, ConfigUsersKeys

def test_requests():
    response = requests.get("https://www.runoob.com/")
    assert response.status_code == 200
    assert len(response.text) > 0
    return response


def test_pycryptodome():
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    data = b"hello world"
    ciphertext, tag = cipher.encrypt_and_digest(data)
    assert ciphertext != data
    return ciphertext

def test_config():
    print("Config:")
    pprint(config.config)
    print("Log Level:", config["log_level"])
    print("Log Retention Days:", config["log_retention_days"])
    print("Retry Attempts:", config["retry_attempts"])

    print("\nSetting config...")
    config["log_level"] = "DEBUG"
    user = config.addUser("LuTong")
    user2 = config.getUser("LuTong")
    assert user.username == user2.username
    user[ConfigUsersKeys.USER_AGENT] = "MyUserAgent"
    print("Config:")
    pprint(config.config)
    pprint(config.listUsername())

    print("\nResetting config...")
    config["log_level"] = "INFO"
    config.removeUser("LuTong")
    print("Config:")
    pprint(config.config)
