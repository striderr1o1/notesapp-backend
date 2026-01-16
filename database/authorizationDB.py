from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
class mongo_db_auth_connector:
    def __init__():
        self.username = os.environ.get("MONGO_USERNAME")
        self.password = os.environ.get("MONGO_PASSWORD")
        self.uri = f"mongodb+srv://{self.username}:{self.password}@cluster0.tiufhor.mongodb.net/?appName=Cluster0"
        self.client = None
        self.database = None
        self.collection = None
        self._connect()
        return

    def _connect(self):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = client["auth"]
        self.collection = self.database["username_passwords"]
        return