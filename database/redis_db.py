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
        key = f"session:{session_id}"

        self.rclient.setex(
            key,
            session_timelimit,
            username
        )

        return session_id