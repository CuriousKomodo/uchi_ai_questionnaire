from typing import List, Dict, Optional

from google.cloud import firestore
from datetime import datetime

from utils import read_json


class FireStore:
    def __init__(self, credential_info: Optional[Dict] = None, credential_info_path: Optional[str] = None):
        if credential_info:
            self.db = firestore.Client.from_service_account_info(credential_info)
        else:
            self.db = firestore.Client.from_service_account_json(credential_info_path)
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
        _, submission_record = self.db.collection('submissions').add({
            "user_id": user_id,
            'email': results["email"],
            'content': results,
        })
        
        # Return the submission document ID
        submission_id = submission_record.path.split("/")[-1]
        return submission_id

    def list_all_users(self) -> List[Dict]:
        users_stream = self.db.collection('users').stream()
        users = []
        for doc in users_stream:
            print('{} => {}'.format(doc.id, doc.to_dict()))
            users.append(doc.to_dict())
        return users


if __name__ == '__main__':
    firestore = FireStore(credential_info_path="firestore-key.json")
    result = read_json("example_result.json")
    firestore.insert_submission(result)