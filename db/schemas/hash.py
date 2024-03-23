import hashlib

class Hash():
    @staticmethod
    def sha256(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        return hashed_password == Hash.sha256(plain_password)
