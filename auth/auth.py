from passlib.context import CryptContext
class Authentication:
    def __init__(self, connector):
        self.database_connector = connector
        self.pwd_context = CryptContext(
                    schemes=["bcrypt"],
                    deprecated="auto"
                )
        return
    
    def _hash_password(self, password):
        return self.pwd_context.hash(password)

    def _create_user(self, username, password, email):
        hashed_password = self._hash_password(password)
        status = self.database_connector.insert_user(username, hashed_password, email)
        return status
    
    def sign_up(self, username, password, email):
        status = self._create_user(username, password, email)
        return status
