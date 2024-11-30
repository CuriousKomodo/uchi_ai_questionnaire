from typing import List, Dict

from google.cloud import firestore
from datetime import datetime

from utils import read_json


class FireStore:
    def __init__(self):
        self.db = firestore.Client.from_service_account_json("firestore-key.json")
        self.users_collection = self.db.collection('users')
        self.submission_collection = self.db.collection('submissions')

    def insert_submission(self, results):
        # Create the new user
        user_fields = {
            "email": results["email"],
            "first_name": results["first_name"],
            'created_at': datetime.now(),
        }
        # Do check to see if the user already exists.
        _, record = self.users_collection.add(user_fields)
        user_id = record.path.split("/")[-1]

        # Store the submission
        results.update({'created_at': datetime.now()})
        self.db.collection('submissions').add({
            "user_id": user_id,
            'email': results["email"],
            'content': results,
        })

    def list_all_users(self) -> List[Dict]:
        users_stream = self.db.collection('users').stream()
        users = []
        for doc in users_stream:
            print('{} => {}'.format(doc.id, doc.to_dict()))
            users.append(doc.to_dict())
        return users


if __name__ == '__main__':
    firestore = FireStore()
    result = read_json("example_result.json")
    firestore.insert_submission(result)