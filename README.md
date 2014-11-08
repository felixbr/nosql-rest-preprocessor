nosql-rest-preprocessor
=======================

A helper module which solves common problems when building rest-apis with nosql backends.

### Examples

```python
from nosql-rest-preprocessor.models import BaseModel

class AddressModel(BaseModel):
    required_attributes = {'street', 'city', 'plz'}

class UserModel(BaseModel):
    required_attributes = {'firstName', 'lastName', 'email'}
    immutable_attributes = {'id'}
    private_attributes = {'password', 'salt'}
    
    # will use AddressModel to validate, merge and prepare the content of the 'address' attribute
    sub_models: {
        'address': AddressModel
    }
```

```python
new_user_from_request = {
    "firstName": "Sepp",
    "lastName": "Huber",
    "email": "sepp.huber@fancepants.com",
    "address": {
        "street": "Bakerstreet 1",
        "city": "London",
        "plz": "12345"
    }
}

# checks required_attributes and raises ValidationError if something's amiss
UserModel.validate(new_user_from_request)

```
```python
user_obj_from_db = db.fetch_user_by_email("sepp.huber@fancepants.com")

# strips out any non-public attributes
response_obj = UserModel.prepare_response(user_obj_from_db)

return Response(response_obj)
```

