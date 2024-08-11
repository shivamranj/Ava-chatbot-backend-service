import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.main import app
from app.models import User
from app.schemas import userCreate, userResponse
from app.database import LocalDbSession
from app.constant import *
from app.models import User, Message
import json




client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = LocalDbSession()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def db_mock():
    return MagicMock(spec=Session)

@pytest.fixture
def redis_mock():
    with patch('app.redis_client') as mock_redis:
        yield mock_redis

@pytest.fixture
def generate_response_mock():
    with patch('app.services.generate_response') as mock_generate_responses:
        yield mock_generate_responses

@patch('app.routes.create_user')

def create_user_test(mock_create_user):
    mock_user_id = '5040841'
    mock_create_user.return_value = userResponse(status_code=200, data={"user_id": mock_user_id})

    response = client.post(CREATE_USER, json={"email": "vhmhbhbjkbk@gmail.com"})
    
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "data": {"user_id": mock_user_id}}

def return_existing_user_id_test(db):
    existing_user = User(email="existinguser@example.com", unique_id="12374567")
    db.add(existing_user)
    db.commit()

    response = client.post(CREATE_USER, json={"email": "existinguser@example.com"})

    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "data": {"user_id": "12374567"}}


@patch('app.routes.chat')
def user_not_found_chat_test(db_mock):
    db_mock.query(User).filter().first.return_value = None

    response = client.post(CHAT, json={"user_id": "12345777", "message": "Hello, bot!"})

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_chat_success(db_mock, redis_mock, generate_response_mock):
    mock_user = User(unique_id="12345767", email="existinguser@example.com")
    db_mock.query(User).filter().first.return_value = mock_user

    user_message = "Hello, bot!"
    bot_reply = "Hello, user!"
    generate_response_mock.return_value = bot_reply

    mock_message_entry = Message(user_id="12345767", user_message=user_message, bot_reply=bot_reply)
    db_mock.query(Message).filter().all.return_value = [mock_message_entry]

    response = client.post(CHAT, json={"user_id": "12345767", "message": user_message})

    assert response.status_code == 200
    assert response.json() == {"reply": bot_reply}

    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

    redis_mock.set.assert_called_once()
    cache_key = "message_history:12345767"
    cached_value = json.loads(redis_mock.set.call_args[0][1])
    assert cached_value[0]['text'] == user_message
    assert cached_value[1]['text'] == bot_reply

