import json
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite_client import client
from appwrite.query import Query
from requests.exceptions import RequestException

databases = Databases(client)

imagesDatabaseId = "676ac66c1ad26ff6b85d"
imagesCollectionId = "676ac66d428f98c5ed1a"

def create_document(database_id, collection_id, data, document_id = ID.unique()):
    try:
        result = databases.create_document(
            database_id=database_id,
            collection_id=collection_id,
            document_id=document_id,
            data=data
        )
    except Exception as e:
        print("Error creating document:", e)

def create_image_document(image_id, isLabled = False):
    create_document(imagesDatabaseId, imagesCollectionId, {"image_id": image_id, "isLabled": isLabled})

def check_image_exists(image_id)-> bool:
    try:
        result = databases.list_documents(database_id=imagesDatabaseId, collection_id=imagesCollectionId, queries=[Query.equal('image_id', image_id)])
        return True
    except Exception as e:
        print("Error checking document:", e)
        return False
    
def is_image_labled(image_id)-> bool:
    try:
        result = databases.list_documents(database_id=imagesDatabaseId, collection_id=imagesCollectionId, queries=[Query.equal('image_id', image_id)])
        return result['documents'][0]['isLabled']
    except Exception as e:
        print("Error checking document:", e)
        return False
    
def update_image_labled(image_id, isLabled, human_score):
    try:
        result = databases.list_documents(database_id=imagesDatabaseId, collection_id=imagesCollectionId, queries=[Query.equal('image_id', image_id)])
        document_id = result['documents'][0]['$id']
        
        result = databases.update_document(
            database_id=imagesDatabaseId,
            collection_id=imagesCollectionId,
            document_id=document_id,
            data={
                "isLabled": isLabled,
                "human_score": json.dumps(human_score),
            }
        )
    except Exception as e:
        raise RequestException()