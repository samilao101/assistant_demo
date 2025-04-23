
from GSAR_functions import document_creator

functions_call = [
{
    "name": "create_document_with_settings", 
    "decription": "based on the type of request being made, build a document.",
    "parameters": {
        "type": "object",
        "properties": {
            "name_update": {
                "type": "string", "enum": ["yes", "no"]
            },
            "address_update": {
                "type": "string", "enum": ["yes", "no"]
            },
            "contact_update": {
                "type": "string", "enum": ["yes", "no"]
            },
            "banking_update": {
                "type": "string", "enum": ["yes", "no"]
            },
            "contact_add": {
                "type": "string", "enum": ["yes", "no"]
            },
            "address_add": {
                "type": "string", "enum": ["yes", "no"]
            },
            "currency_update": {
                "type": "string", "enum": ["yes", "no"]
            }
        }, 
        "required": ["name_update", "address_update", "contact_update", "banking_update", "contact_add", "address_add", "currency_update"]
    }

}

]

def create_document_with_settings(document_settings):
    print(document_settings)
    document_creator.create_documents(document_settings)
    document_creator.create_eform_documents(document_settings)

    
