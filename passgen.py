import bcrypt
from getpass import getpass

password = getpass("Anna uusi salasana: ")

hashed = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt(rounds=12, prefix=b"2b")
)

print(hashed.decode("utf-8"))
