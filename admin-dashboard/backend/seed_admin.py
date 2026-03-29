import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    # Check if admin exists
    existing = await db.admins.find_one({"username": "admin"})
    if existing:
        print("✅ Admin user already exists")
        return
    
    # Create super admin
    hashed_password = pwd_context.hash("admin123")
    await db.admins.insert_one({
        "username": "admin",
        "password": hashed_password,
        "role": "super_admin"
    })
    print("✅ Super Admin created!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Role: super_admin")
    print("\n⚠️  PLEASE CHANGE THE PASSWORD AFTER FIRST LOGIN!")

if __name__ == "__main__":
    asyncio.run(create_admin())
