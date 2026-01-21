from passlib.context import CryptContext
from fastapi import Request, HTTPException
class Authentication:
    def __init__(self, mdb_connector, redis_connector):
        self.database_connector = mdb_connector
        self.redis_connector = redis_connector
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
        if status == False:
            raise HTTPException(status_code = 401, detail = "User exists")

        return status

    def login(self, username, password):
        #create session
        
        user_data = self.database_connector.find_user(username)
        if not user_data:
            return {"status": False}
        if(user_data["username"]== username and self.pwd_context.verify(password, user_data["password"])):
            session_id = self.redis_connector.create_session(username)
            return {"status": True, "session_id": session_id}
        else:
            return {"status": False}

    def validate_session(self, request: Request):
        session_id = request.cookies.get("session_id")
        print(request)
        if not session_id:
            raise HTTPException(status_code = 401, detail = "Not authenticated, no session id included")
        username_from_session = self.redis_connector.get_user_from_id(session_id)
        if not username_from_session:
            raise HTTPException(status_code = 401, detail = "Not authenticated, user not found in sessions db")
        
        userdata = self.database_connector.find_user(username_from_session)
        if not userdata:
            raise HTTPException(status_code=401, detail = "No such user found")

        return userdata

    def logout(self, request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code = 401, detail = "Not authenticated, no session id included")
        status = self.redis_connector.delete_session(session_id)
        if status == True:
            return {"status": True}
        return {"status": False }
    
    def enterID_in_userdata(self,username,ID):
        status = self.database_connector.enter_id_in_userdata(username, ID)

        return status



