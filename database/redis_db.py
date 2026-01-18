import redis
import uuid
from datetime import datetime, timedelta
import os
class redis_connector:
    def __init__(self):
        self.rclient = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), decode_responses=True)
        
        return

    def create_session(self, username):
        session_id = str(uuid.uuid4())
        session_timelimit = timedelta(days=7)
        key = session_id

        self.rclient.setex(
            key,
            session_timelimit,
            username
        )

        return session_id

    def get_user_from_id(self, sessionid):
        user_id = self.rclient.get(sessionid)
        print(user_id)
        return user_id
   
    def delete_session(self, sessionid):
        if(self.rclient.delete(sessionid)):
            return True
        return False
