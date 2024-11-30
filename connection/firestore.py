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
        user_fields= {
            "email": results["email"],
            'time_created': datetime.now()
        }
        # Do check to see if the user already exists.
        user_id = self.users_collection.document(results["email"]).set(user_fields)

        # Store the submission
        doc_ref = self.db.collection('submissions').document('test')
        results.update({'time_created': datetime.now()})
        doc_ref.set({
            "user_id": user_id,
            'email': results["email"],
            'content': results,
        })

    def list_all_users(self):
        users_ref = self.db.collection('users')
        for doc in users_ref.stream():
            print('{} => {}'.format(doc.id, doc.to_dict()))


if __name__ == '__main__':
    firestore = FireStore()
    result = read_json("example_config.json")
    firestore.insert_submission(result)