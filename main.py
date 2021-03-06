# Python
import json
from typing import Optional, List
from uuid import UUID
from datetime import date
from datetime import datetime

# Pydantic
from pydantic import BaseModel 
from pydantic import EmailStr
from pydantic import Field

# FastAPI
from fastapi import HTTPException
from fastapi import FastAPI
from fastapi import status
from fastapi import Body, Form, Path

app = FastAPI()

# Models

class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(
        ...,
        example="miguel@example.com"
        )

class UserLogin(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        max_length=64
    )

class User(UserBase):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    birth_date: Optional[date] = Field(default=None)

class UserRegister(User):
    password: str = Field(
        ..., 
        min_length=8,
        max_length=64,
        example="holasoymiguel"
    )

class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
        )
    created_at: datetime = Field(default=datetime.now())
    update_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)

# Path Operations

## Users

### Register a user
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    tags=["Users"]
)
def signup(user: UserRegister = Body(...)):
    """
    Signup

    This path operation register a user inte app

    Parameters:
    - Request body parameter
        - **user: UserRegister**

    Returns a json with the basic user information:
    - **user_id: UUID**
    - **email: EmailStr**
    - **first_name: str**
    - **last_name: str**
    - **birth_date: date**
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return user

### Login a user
@app.post(
    path="/login",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    tags=["Users"]
)
# def login(email: str = Form(...), password: str = Form(...)):
def login(email: str = Form(...), password: str = Form(...)):

    """
    Login

    This path operation initialize a session

    Parameters: 
    - Request Body parameter
        - email: str
        - password: str

    Returns a User
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        for _user in results:
            if (_user["email"] == email) and (_user['password'] == password):
                try:
                    return User(
                        user_id=_user["user_id"], 
                        email=email, 
                        first_name= _user["first_name"],
                        last_name= _user["last_name"],
                        birth_date= _user["birth_date"]
                        ) 
                except:
                    continue
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password."
        )

### Show all users
@app.get(
    path="/users",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Show all users",
    tags=["Users"]
)
def show_all_users():
    """
    This path operation show all users in the app

    Parameters:
    -

    Returns a json list with all users in the app with the following keys:
    - **user_id: UUID**
    - **email: EmailStr**
    - **first_name: str**
    - **last_name: str**
    - **birth_date: date**
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results


### Show a user
@app.get(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Show a user",
    tags=["Users"]
)
def show_a_user(user_id: str = Path(...)):
    """
    This path operation shows the data of a user by it's ID.

    Parameters:
    - Request body parameters:
        - first_name: str
        - last_name: str

    Returns a User model.
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        for _user in results:
            if _user["user_id"] == user_id:
                return User(
                        user_id=_user["user_id"], 
                        email=_user["email"], 
                        first_name= _user["first_name"],
                        last_name= _user["last_name"],
                        birth_date= _user["birth_date"]
                        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="??This person doesn't exists!"
        )

### Delete a user
@app.delete(
    path="/users/{user_id}/delete",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    tags=["Users"]
)
def delete_a_user(user_id: str = Path(...)):
    """
    This path operation receives an ID and deletes a user from the database.

    Parameters:
    - Request body parameters:
        - user_id: str

    Returns a json with the deleted user data.
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        for _user in results:
            if _user["user_id"] == user_id:
                results.remove(_user)
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return User(
                    user_id= _user["user_id"],
                    email= _user["email"],
                    first_name= _user["first_name"],
                    last_name= _user["last_name"],
                    birth_date= _user["birth_date"]
                )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="??This person doesn't exists!"
        )
       

### Upddate a user
@app.put(
    path="/users/{user_id}/update",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    tags=["Users"]
)
def update_a_user(user_id: str = Path(...), user: UserRegister = Body(...)):
    """
    This path operation updated the information of a user.

    Parameters:
    - user_id: str

    Returns a json with the updated imformation of the user
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        user_d = user.dict()
        for _user in results:
            if _user["user_id"] == user_id:
                _user["user_id"] = user_id
                _user["email"] = str(user_d["email"])
                _user["first_name"] = user_d["first_name"]
                _user["last_name"] = user_d["last_name"]
                _user["birth_date"] = str(user_d["birth_date"])
                _user["password"] = user_d["password"]
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return _user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This person does not exists!"
        )


## Tweets

### Show all tweets
@app.get(
    path="/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets",
    tags=["Tweets"]
    )
def home():
    """
    This path operation show all tweets in the app

    Parameters:
    -

    Returns a json list with all tweets in the app with the following keys:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - update_at: Optional[datetime]
    - by: User
    """
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Post a tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a tweet",
    tags=["Tweets"]
)
def post(tweet: Tweet = Body(...)):
    """
    Post a Tweet

    This path operation post a tweet in the app

    Parameters:
    - Request body parameter
        - **tweet: Tweet**

    Returns a json with the basic tweet information:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - update_at: Optional[datetime]
    - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["update_at"] = str(tweet_dict["update_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return tweet

### Show a tweet
@app.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a tweet",
    tags=["Tweets"]
)
def show_a_tweet(tweet_id: str = Path(...)):
    """
    This path operation shows a tweet.

    Parameters:
    - tweet_id: str

    Returns a json with the information of the tweet
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        for _tweet in results:
            if _tweet["tweet_id"] == tweet_id:
                return _tweet
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="This tweet does not exists."
            )

### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"]
)
def delete_a_tweet(tweet_id: str = Path(...)):
    """
    This path operation deletes a tweet

    Parameters:
    - tweet_id: str

    Returns a json with the information of the deleted tweet
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        for _tweet in results:
            if _tweet["tweet_id"] == tweet_id:
                results.remove(_tweet)
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return _tweet
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="??This tweet doesn't exists!"
        )

### Update a tweet
@app.put(
    path="/tweets/{tweet_id}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a tweet",
    tags=["Tweets"]
)
def update_a_tweet(tweet_id: str = Path(...), tweet: Tweet = Body(...)):
    """
    This path operation updates the content of a tweet

    Parameters:
    - tweet_id: str

    Returns a json with the information of the updated tweet.
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_d = tweet.dict()
        for _tweet in results:
            if _tweet["tweet_id"] == tweet_id:
                _tweet["tweet_id"] = tweet_id
                _tweet["content"] = tweet_d["content"]
                _tweet["update_at"] = str(tweet_d["update_at"])
                                
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return _tweet
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This person does not exists!"
        )