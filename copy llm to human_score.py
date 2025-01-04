from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def copy_llm_response_to_human_score():
    # Initialize the Appwrite client
    client = Client()
    client.set_endpoint('https://cloud.appwrite.io/v1')
    client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
    client.set_key(os.getenv('APPWRITE_API_KEY'))

    # Initialize the database service
    databases = Databases(client)

    # Database and Collection IDs
    database_id = "676ac66c1ad26ff6b85d"
    collection_id = "676ac66d428f98c5ed1a"

    try:
        offset = 0
        limit = 25  # Maximum limit per request
        total_documents = 1  # Initial value to enter the loop

        while offset < total_documents:
            # Fetch documents with pagination
            response = databases.list_documents(database_id, collection_id, queries=[
                Query.offset(offset),
                Query.limit(limit),
                Query.is_null('human_score')
            ])
            documents = response['documents']
            total_documents = response['total']  # Total number of documents in the collection

            print(f"Processing batch: {offset + 1} to {offset + len(documents)} of {total_documents}")

            # Iterate through the documents in the current batch
            for index, document in enumerate(documents):
                if 'llm_response' in document:
                    document_id = document['$id']
                    updated_data = {
                        'human_score': document['llm_response']
                    }
                    # Update the document
                    res = databases.update_document(database_id, collection_id, document_id, updated_data)
                    print(f"Updated document {document_id}: {res}")

            # Increment offset for the next batch
            offset += limit

        print("Successfully updated all documents.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function
copy_llm_response_to_human_score()
