from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId
import re

# ================= ENV =================
load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "test_database")

print("=== STARTUP CHECK ===")
print("MONGO_URL:", MONGO_URL)
print("DB_NAME:", DB_NAME)
print("=====================")

# ================= APP =================
app = FastAPI(title="Arjun AI API")
api_router = APIRouter(prefix="/api")

# ================= DB =================
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db["users"]

# ================= SECURITY =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.environ.get("JWT_SECRET", "secret")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

# ================= MODELS =================
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessage(BaseModel):
    message: str
    mode: Optional[str] = "general"
    character: Optional[str] = "arjun"

class UpdateProfileRequest(BaseModel):
    name: str

# ================= HELPERS =================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(p, h):
    return pwd_context.verify(p, h)

def create_access_token(data: dict):
    data.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await users_collection.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ================= AUTH =================
@api_router.post("/auth/register")
async def register(user: UserRegister):
    try:
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = hash_password(user.password)

        await users_collection.insert_one({
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_premium": False,
            "total_chats": 0
        })

        return {"message": "User registered successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    try:
        user = await users_collection.find_one({"email": user_data.email})

        if not user or not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": str(user["_id"])})
        return {"access_token": token}

    except HTTPException:
        raise
    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

# ================= PROFILE =================
@api_router.get("/profile")
async def profile(user=Depends(get_current_user)):
    return {
        "name": user["name"],
        "email": user["email"],
        "is_premium": user.get("is_premium", False),
        "total_chats": user.get("total_chats", 0)
    }

@api_router.put("/profile")
async def update_profile(data: UpdateProfileRequest, user=Depends(get_current_user)):
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"name": data.name}}
    )
    return {"message": "Updated"}

# ================= CHAT =================
async def get_ai_response(message):
    try:
        from openai import OpenAI
        ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Arjun, a wise friend inspired by the Bhagavad Gita."},
                {"role": "user", "content": message}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI ERROR:", e)
        return "Something went wrong with AI response"

@api_router.post("/chat/send")
async def chat(message_data: ChatMessage, user=Depends(get_current_user)):
    ai_response = await get_ai_response(message_data.message)
    await db.chats.insert_one({
        "user_id": user["_id"],
        "message": message_data.message,
        "response": ai_response,
        "timestamp": datetime.utcnow()
    })
    return {"response": ai_response}

@api_router.get("/chat/history")
async def chat_history(user=Depends(get_current_user)):
    chats = await db.chats.find(
        {"user_id": user["_id"]}
    ).sort("timestamp", -1).to_list(50)
    for c in chats:
        c["_id"] = str(c["_id"])
        c["user_id"] = str(c["user_id"])
    return chats

# ================= HEALTH =================
@api_router.get("/health")
async def health():
    try:
        await client.admin.command('ping')
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "ok", "database": "error", "detail": str(e)}

# ================= MIDDLEWARE =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
