from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId
import secrets
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 10080))

# LLM Settings
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app
app = FastAPI(title="Arjun AI API")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    id: str
    message: str
    response: str
    timestamp: datetime

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    total_chats: int

# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

async def get_ai_response(message: str, user_id: str) -> str:
    """Get AI response using Emergent LLM"""
    try:
        # Create chat instance
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"user_{user_id}",
            system_message="""You are Arjun, a wise spiritual guide based on the teachings of the Bhagavad Gita. 
            You provide guidance, wisdom, and emotional support rooted in the timeless principles of the Gita.
            Your responses should be:
            - Compassionate and understanding
            - Rooted in Gita's teachings where relevant
            - Practical and applicable to modern life
            - Brief but meaningful (2-3 sentences usually)
            - Include occasional Sanskrit quotes when appropriate
            
            Remember: You are not just an AI, you are a spiritual companion on the user's journey."""
        ).with_model("openai", "gpt-5.2")
        
        # Send message
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return "I apologize, but I'm having trouble connecting to my wisdom source. Please try again in a moment."

# Auth Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = {
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "total_chats": 0
        }
        
        result = await db.users.insert_one(new_user)
        
        # Create access token
        access_token = create_access_token({"sub": str(result.inserted_id)})
        
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(result.inserted_id),
                "name": user_data.name,
                "email": user_data.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    """Login user"""
    try:
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token({"sub": str(user["_id"])})
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPassword):
    """Send OTP for password reset"""
    try:
        user = await db.users.find_one({"email": data.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in database
        await db.otp_codes.update_one(
            {"email": data.email},
            {
                "$set": {
                    "email": data.email,
                    "otp": otp,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(minutes=10)
                }
            },
            upsert=True
        )
        
        # In production, send OTP via email
        # For now, we'll return it in the response (NOT SECURE IN PRODUCTION)
        logger.info(f"OTP for {data.email}: {otp}")
        
        return {
            "message": "OTP sent successfully",
            "otp": otp  # Remove this in production
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/reset-password")
async def reset_password(data: ResetPassword):
    """Reset password using OTP"""
    try:
        # Verify OTP
        otp_record = await db.otp_codes.find_one({
            "email": data.email,
            "otp": data.otp
        })
        
        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        if otp_record["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")
        
        # Update password
        hashed_password = hash_password(data.new_password)
        await db.users.update_one(
            {"email": data.email},
            {"$set": {"password": hashed_password}}
        )
        
        # Delete used OTP
        await db.otp_codes.delete_one({"email": data.email})
        
        return {"message": "Password reset successful"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Routes
@api_router.post("/chat/send")
async def send_chat_message(
    message_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to Arjun AI"""
    try:
        user_id = str(current_user["_id"])
        
        # Get AI response
        ai_response = await get_ai_response(message_data.message, user_id)
        
        # Save chat to database
        chat_entry = {
            "user_id": ObjectId(user_id),
            "message": message_data.message,
            "response": ai_response,
            "timestamp": datetime.utcnow()
        }
        
        result = await db.chats.insert_one(chat_entry)
        
        # Update user's total chats count
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"total_chats": 1}}
        )
        
        return {
            "id": str(result.inserted_id),
            "message": message_data.message,
            "response": ai_response,
            "timestamp": chat_entry["timestamp"]
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for current user"""
    try:
        user_id = str(current_user["_id"])
        
        chats = await db.chats.find(
            {"user_id": ObjectId(user_id)}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return [{
            "id": str(chat["_id"]),
            "message": chat["message"],
            "response": chat["response"],
            "timestamp": chat["timestamp"]
        } for chat in chats]
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/chat/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific chat"""
    try:
        user_id = str(current_user["_id"])
        
        result = await db.chats.delete_one({
            "_id": ObjectId(chat_id),
            "user_id": ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Profile Routes
@api_router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    try:
        return {
            "id": str(current_user["_id"]),
            "name": current_user["name"],
            "email": current_user["email"],
            "created_at": current_user["created_at"],
            "total_chats": current_user.get("total_chats", 0)
        }
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/profile")
async def update_profile(
    name: str,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        user_id = str(current_user["_id"])
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"name": name}}
        )
        
        return {"message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Arjun AI API"}

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
