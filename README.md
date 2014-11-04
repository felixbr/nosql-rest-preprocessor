nosql-rest-preprocessor
=======================

A helper module which solves common problems when building rest-apis with nosql backends.

### Examples

```python
from nosql-rest-preprocessor.models import BaseModel

class UserModel(BaseModel):
    required_attributes = {'firstName', 'lastName', 'email'}
    immutable_attributes = {'id'}
    non_public_attributes = {'password', 'salt'}
    
```

```python
new_user_from_request = {
    "firstName": "Sepp",
    "lastName": "Huber",
    "email": "sepp.huber@fancepants.com"
}

UserModel.validate(new_user_from_request)  # checks required_attributes and raises ValidationError if something's amiss

```
```python
user_obj_from_db = db.fetch_user_by_email("sepp.huber@fancepants.com")

response_obj = UserModel.prepare_response(user_obj_from_db)  # strips out any non-public attributes

return Response(response_obj)
```

