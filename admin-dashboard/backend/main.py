from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Settings
JWT_SECRET = os.environ.get('ADMIN_JWT_SECRET', 'admin-secret-key-change-this')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = 480  # 8 hours

app = FastAPI(title="Arjun AI Admin Dashboard API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUser(BaseModel):
    username: str
    password: str
    role: str = "admin"  # super_admin or admin

class AIConfig(BaseModel):
    system_prompt: str
    model: str
    tone: str

class Notification(BaseModel):
    title: str
    message: str
    target: str = "all"  # all or specific user_id

# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_admin_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        admin = await db.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        return admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Admin Authentication
@app.post("/api/admin/login")
async def admin_login(credentials: AdminLogin):
    admin = await db.admins.find_one({"username": credentials.username})
    if not admin or not verify_password(credentials.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Log login
    await db.admin_logs.insert_one({
        "admin_id": admin["_id"],
        "action": "login",
        "timestamp": datetime.utcnow()
    })
    
    token = create_admin_token({"sub": str(admin["_id"]), "role": admin["role"]})
    return {
        "access_token": token,
        "admin": {
            "id": str(admin["_id"]),
            "username": admin["username"],
            "role": admin["role"]
        }
    }

# Dashboard Overview
@app.get("/api/admin/overview")
async def get_overview(admin: dict = Depends(get_current_admin)):
    total_users = await db.users.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_feedback = await db.feedback.count_documents({})
    
    # Active users (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = await db.users.count_documents({
        "last_activity_date": {"$gte": week_ago}
    })
    
    # Today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
    today_users = await db.users.count_documents({
        "created_at": {"$gte": today_start}
    })
    today_chats = await db.chats.count_documents({
        "timestamp": {"$gte": today_start}
    })
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_chats": total_chats,
        "total_feedback": total_feedback,
        "today_users": today_users,
        "today_chats": today_chats
    }

# User Management
@app.get("/api/admin/users")
async def get_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    query = {}
    if search:
        query = {"$or": [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]}
    
    users = await db.users.find(query).skip(skip).limit(limit).to_list(length=limit)
    total = await db.users.count_documents(query)
    
    return {
        "users": [{
            "id": str(u["_id"]),
            "name": u["name"],
            "email": u["email"],
            "created_at": u["created_at"],
            "total_chats": u.get("total_chats", 0),
            "current_streak": u.get("current_streak", 0)
        } for u in users],
        "total": total
    }

@app.get("/api/admin/users/{user_id}")
async def get_user_details(user_id: str, admin: dict = Depends(get_current_admin)):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's chats
    chats = await db.chats.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1).limit(10).to_list(10)
    
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
        "total_chats": user.get("total_chats", 0),
        "current_streak": user.get("current_streak", 0),
        "longest_streak": user.get("longest_streak", 0),
        "recent_chats": [{
            "id": str(c["_id"]),
            "message": c["message"],
            "response": c["response"],
            "timestamp": c["timestamp"]
        } for c in chats]
    }

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_current_admin)):
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can delete users")
    
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.chats.delete_many({"user_id": ObjectId(user_id)})
    return {"message": "User deleted successfully"}

# Chat Management
@app.get("/api/admin/chats")
async def get_all_chats(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    query = {}
    if user_id:
        query = {"user_id": ObjectId(user_id)}
    
    chats = await db.chats.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    # Get user info for each chat
    result = []
    for chat in chats:
        user = await db.users.find_one({"_id": chat["user_id"]})
        result.append({
            "id": str(chat["_id"]),
            "user_name": user["name"] if user else "Unknown",
            "user_email": user["email"] if user else "Unknown",
            "message": chat["message"],
            "response": chat["response"],
            "mode": chat.get("mode", "general"),
            "timestamp": chat["timestamp"]
        })
    
    return {"chats": result}

@app.delete("/api/admin/chats/{chat_id}")
async def delete_chat(chat_id: str, admin: dict = Depends(get_current_admin)):
    await db.chats.delete_one({"_id": ObjectId(chat_id)})
    return {"message": "Chat deleted"}

# Analytics
@app.get("/api/admin/analytics")
async def get_analytics(admin: dict = Depends(get_current_admin)):
    # Last 7 days stats
    days = 7
    stats = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        start = date.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        
        users = await db.users.count_documents({
            "created_at": {"$gte": start, "$lt": end}
        })
        chats = await db.chats.count_documents({
            "timestamp": {"$gte": start, "$lt": end}
        })
        
        stats.append({
            "date": start.strftime("%Y-%m-%d"),
            "users": users,
            "chats": chats
        })
    
    return {"stats": list(reversed(stats))}

# AI Configuration
@app.get("/api/admin/ai-config")
async def get_ai_config(admin: dict = Depends(get_current_admin)):
    config = await db.ai_config.find_one({"type": "default"})
    if not config:
        return {
            "system_prompt": "Default Arjun AI prompt",
            "model": "gpt-5.2",
            "tone": "spiritual"
        }
    return config

@app.put("/api/admin/ai-config")
async def update_ai_config(config: AIConfig, admin: dict = Depends(get_current_admin)):
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can update AI config")
    
    await db.ai_config.update_one(
        {"type": "default"},
        {"$set": {
            "system_prompt": config.system_prompt,
            "model": config.model,
            "tone": config.tone,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )
    return {"message": "AI config updated"}

# Feedback Management
@app.get("/api/admin/feedback")
async def get_feedback(skip: int = 0, limit: int = 50, admin: dict = Depends(get_current_admin)):
    feedback_list = await db.feedback.find().sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    result = []
    for f in feedback_list:
        result.append({
            "id": str(f["_id"]),
            "user_name": f.get("user_name", "Unknown"),
            "user_email": f.get("user_email", "Unknown"),
            "type": f["type"],
            "message": f["message"],
            "contact_preference": f["contact_preference"],
            "timestamp": f["timestamp"],
            "status": f.get("status", "pending")
        })
    
    return {"feedback": result}

# Payment Management
@app.get("/api/admin/payments")
async def get_payments(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    admin: dict = Depends(get_current_admin)
):
    """Get all payment submissions with optional status filter"""
    query = {}
    if status:
        query["status"] = status
    
    payments = await db.payments.find(query).sort("submitted_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.payments.count_documents(query)
    
    result = []
    for p in payments:
        result.append({
            "id": str(p["_id"]),
            "user_name": p.get("user_name", "Unknown"),
            "user_email": p.get("user_email", "Unknown"),
            "plan": p.get("plan", "Unknown"),
            "amount": p.get("amount", 0),
            "transaction_id": p.get("transaction_id", ""),
            "payment_method": p.get("payment_method", "manual_upi"),
            "status": p.get("status", "pending"),
            "submitted_at": p.get("submitted_at", p.get("created_at")),
            "verified_at": p.get("verified_at"),
            "auto_renew": p.get("auto_renew", False)
        })
    
    return {"payments": result, "total": total}

@app.put("/api/admin/payments/{payment_id}/approve")
async def approve_payment(payment_id: str, admin: dict = Depends(get_current_admin)):
    """Approve manual payment and activate premium"""
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can approve payments")
    
    try:
        # Get payment record
        payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Activate premium for user
        user_id = payment["user_id"]
        expire_date = datetime.utcnow() + timedelta(days=30)
        
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "is_premium": True,
                    "premium_expires": expire_date,
                    "premium_activated_at": datetime.utcnow()
                }
            }
        )
        
        # Update payment status
        await db.payments.update_one(
            {"_id": ObjectId(payment_id)},
            {
                "$set": {
                    "status": "approved",
                    "verified_at": datetime.utcnow(),
                    "verified_by": str(admin["_id"])
                }
            }
        )
        
        return {"message": "Payment approved and premium activated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/payments/{payment_id}/reject")
async def reject_payment(
    payment_id: str,
    reason: str = "Invalid transaction",
    admin: dict = Depends(get_current_admin)
):
    """Reject manual payment"""
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can reject payments")
    
    await db.payments.update_one(
        {"_id": ObjectId(payment_id)},
        {
            "$set": {
                "status": "rejected",
                "rejected_at": datetime.utcnow(),
                "rejected_by": str(admin["_id"]),
                "rejection_reason": reason
            }
        }
    )
    
    return {"message": "Payment rejected"}

@app.get("/api/admin/revenue-stats")
async def get_revenue_stats(admin: dict = Depends(get_current_admin)):
    """Get revenue statistics"""
    # Total revenue from approved/success payments
    approved_payments = await db.payments.find({"status": {"$in": ["approved", "success"]}}).to_list(1000)
    
    total_revenue = sum(p.get("amount", 0) for p in approved_payments)
    
    # Count by payment method
    upi_count = len([p for p in approved_payments if p.get("payment_method") == "manual_upi"])
    razorpay_count = len([p for p in approved_payments if p.get("payment_method") == "razorpay"])
    
    # Pending payments
    pending_count = await db.payments.count_documents({"status": "pending"})
    pending_revenue = sum(p.get("amount", 0) for p in await db.payments.find({"status": "pending"}).to_list(100))
    
    # Premium users count
    premium_users = await db.users.count_documents({"is_premium": True})
    
    return {
        "total_revenue": total_revenue,
        "total_transactions": len(approved_payments),
        "upi_transactions": upi_count,
        "razorpay_transactions": razorpay_count,
        "pending_approvals": pending_count,
        "pending_revenue": pending_revenue,
        "premium_users": premium_users
    }

# Health Check
@app.get("/api/admin/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)