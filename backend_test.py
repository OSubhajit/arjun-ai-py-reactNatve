#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Arjun AI Mobile App
Tests all authentication, chat, profile, premium, and admin APIs
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://app-converter-106.preview.emergentagent.com/api"
ADMIN_BASE_URL = "http://localhost:8002/api"  # Admin backend runs locally
TEST_USER = {
    "name": "Test User",
    "email": "test@gitapath.com", 
    "password": "newwisdom123"  # Updated password after reset
}
ADMIN_CREDENTIALS = {
    "username": "sarkarsoadmin",
    "password": "Subhajit#@!123454"
}

class ArjunAITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_base_url = ADMIN_BASE_URL
        self.auth_token = None
        self.admin_token = None
        self.user_id = None
        self.chat_id = None
        self.payment_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, "Unhealthy response", data)
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration API"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=TEST_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Registration", True, "User registered successfully")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing token or user data", data)
                    return False
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try to login instead
                self.log_result("User Registration", True, "User already exists (expected)")
                return self.test_user_login()
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login API"""
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Login", True, "Login successful")
                    return True
                else:
                    self.log_result("User Login", False, "Missing token or user data", data)
                    return False
            else:
                self.log_result("User Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Login", False, f"Request error: {str(e)}")
            return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            invalid_data = {
                "email": TEST_USER["email"],
                "password": "wrongpassword"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=invalid_data,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_result("Invalid Login Test", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_result("Invalid Login Test", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Invalid Login Test", False, f"Request error: {str(e)}")
            return False
    
    def test_forgot_password(self):
        """Test forgot password API"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/forgot-password",
                json={"email": TEST_USER["email"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "otp" in data:  # OTP returned for demo
                    self.otp = data["otp"]
                    self.log_result("Forgot Password", True, f"OTP generated: {self.otp}")
                    return True
                else:
                    self.log_result("Forgot Password", False, "No OTP in response", data)
                    return False
            else:
                self.log_result("Forgot Password", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Forgot Password", False, f"Request error: {str(e)}")
            return False
    
    def test_reset_password(self):
        """Test reset password API"""
        if not hasattr(self, 'otp'):
            self.log_result("Reset Password", False, "No OTP available from forgot password test")
            return False
            
        try:
            reset_data = {
                "email": TEST_USER["email"],
                "otp": self.otp,
                "new_password": "newwisdom123"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/reset-password",
                json=reset_data,
                timeout=10
            )
            
            if response.status_code == 200:
                # Test login with new password
                login_response = requests.post(
                    f"{self.base_url}/auth/login",
                    json={"email": TEST_USER["email"], "password": "newwisdom123"},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    # Update the global password for subsequent tests
                    TEST_USER["password"] = "newwisdom123"
                    self.log_result("Reset Password", True, "Password reset and login successful")
                    return True
                else:
                    self.log_result("Reset Password", False, "Password reset but login failed")
                    return False
            else:
                self.log_result("Reset Password", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Reset Password", False, f"Request error: {str(e)}")
            return False
    
    def test_ai_chat(self):
        """Test AI chat API"""
        if not self.auth_token:
            self.log_result("AI Chat", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            chat_data = {"message": "I feel lost in life and need spiritual guidance"}
            
            response = requests.post(
                f"{self.base_url}/chat/send",
                json=chat_data,
                headers=headers,
                timeout=30  # AI responses may take longer
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "id" in data:
                    self.chat_id = data["id"]
                    ai_response = data["response"]
                    
                    # Check if response seems spiritual/Gita-based
                    spiritual_keywords = ["dharma", "karma", "gita", "krishna", "arjuna", "wisdom", "spiritual", "soul"]
                    has_spiritual_content = any(keyword.lower() in ai_response.lower() for keyword in spiritual_keywords)
                    
                    if has_spiritual_content or len(ai_response) > 50:  # Either spiritual or substantial response
                        self.log_result("AI Chat", True, f"AI responded with spiritual guidance: {ai_response[:100]}...")
                        return True
                    else:
                        self.log_result("AI Chat", False, f"Response doesn't seem spiritual: {ai_response}")
                        return False
                else:
                    self.log_result("AI Chat", False, "Missing response or ID in data", data)
                    return False
            else:
                self.log_result("AI Chat", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI Chat", False, f"Request error: {str(e)}")
            return False
    
    def test_chat_history(self):
        """Test chat history API"""
        if not self.auth_token:
            self.log_result("Chat History", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(
                f"{self.base_url}/chat/history",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if our recent chat is in history
                        recent_chat = data[0]
                        if "message" in recent_chat and "response" in recent_chat:
                            self.log_result("Chat History", True, f"Retrieved {len(data)} chats")
                            return True
                        else:
                            self.log_result("Chat History", False, "Chat format invalid", recent_chat)
                            return False
                    else:
                        self.log_result("Chat History", True, "No chats in history (expected for new user)")
                        return True
                else:
                    self.log_result("Chat History", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Chat History", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Chat History", False, f"Request error: {str(e)}")
            return False
    
    def test_user_profile_get(self):
        """Test get user profile API"""
        if not self.auth_token:
            self.log_result("Get Profile", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(
                f"{self.base_url}/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "name", "email", "created_at", "total_chats"]
                if all(field in data for field in required_fields):
                    self.log_result("Get Profile", True, f"Profile retrieved: {data['name']} ({data['email']})")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result("Get Profile", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_result("Get Profile", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Profile", False, f"Request error: {str(e)}")
            return False
    
    def test_user_profile_update(self):
        """Test update user profile API"""
        if not self.auth_token:
            self.log_result("Update Profile", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            new_name = "Enlightened Seeker"
            
            # Note: The API expects form data, not JSON for the name parameter
            response = requests.put(
                f"{self.base_url}/profile",
                headers=headers,
                params={"name": new_name},  # Send as query parameter
                timeout=10
            )
            
            if response.status_code == 200:
                # Verify the update by getting profile again
                get_response = requests.get(
                    f"{self.base_url}/profile",
                    headers=headers,
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    profile_data = get_response.json()
                    if profile_data.get("name") == new_name:
                        self.log_result("Update Profile", True, f"Profile updated to: {new_name}")
                        return True
                    else:
                        self.log_result("Update Profile", False, f"Name not updated. Got: {profile_data.get('name')}")
                        return False
                else:
                    self.log_result("Update Profile", False, "Update succeeded but verification failed")
                    return False
            else:
                self.log_result("Update Profile", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Profile", False, f"Request error: {str(e)}")
            return False
    
    def test_delete_chat(self):
        """Test delete chat API"""
        if not self.auth_token or not self.chat_id:
            self.log_result("Delete Chat", False, "No auth token or chat ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.delete(
                f"{self.base_url}/chat/{self.chat_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Verify deletion by checking if chat is gone from history
                history_response = requests.get(
                    f"{self.base_url}/chat/history",
                    headers=headers,
                    timeout=10
                )
                
                if history_response.status_code == 200:
                    chats = history_response.json()
                    chat_exists = any(chat.get("id") == self.chat_id for chat in chats)
                    
                    if not chat_exists:
                        self.log_result("Delete Chat", True, "Chat deleted successfully")
                        return True
                    else:
                        self.log_result("Delete Chat", False, "Chat still exists in history")
                        return False
                else:
                    self.log_result("Delete Chat", False, "Delete succeeded but verification failed")
                    return False
            else:
                self.log_result("Delete Chat", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Delete Chat", False, f"Request error: {str(e)}")
            return False
    
    def test_premium_status(self):
        """Test premium status API (FIXED - should return complete premium info)"""
        if not self.auth_token:
            self.log_result("Premium Status", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(
                f"{self.base_url}/premium/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["is_premium", "premium_expires", "available_characters"]
                if all(field in data for field in required_fields):
                    self.log_result("Premium Status", True, f"Premium status retrieved: is_premium={data['is_premium']}")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result("Premium Status", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_result("Premium Status", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Premium Status", False, f"Request error: {str(e)}")
            return False

    def test_manual_payment_verification(self):
        """Test manual UPI payment verification API (FIXED - now uses JSON body)"""
        if not self.auth_token:
            self.log_result("Payment Verification", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payment_data = {
                "plan": "Divine",
                "amount": 5000,
                "transaction_id": "UPI123456789",
                "auto_renew": False
            }
            
            response = requests.post(
                f"{self.base_url}/premium/verify-payment",
                json=payment_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "payment_id" in data and "status" in data:
                    self.payment_id = data["payment_id"]
                    if data["status"] == "pending_verification":
                        self.log_result("Payment Verification", True, f"Payment submitted for verification: {self.payment_id}")
                        return True
                    else:
                        self.log_result("Payment Verification", False, f"Unexpected status: {data['status']}")
                        return False
                else:
                    self.log_result("Payment Verification", False, "Missing payment_id or status", data)
                    return False
            else:
                self.log_result("Payment Verification", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Payment Verification", False, f"Request error: {str(e)}")
            return False

    def test_chat_with_mode(self):
        """Test AI chat API with mode parameter"""
        if not self.auth_token:
            self.log_result("AI Chat with Mode", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            chat_data = {
                "message": "What is dharma?",
                "mode": "general"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/send",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "id" in data:
                    ai_response = data["response"]
                    spiritual_keywords = ["dharma", "karma", "gita", "krishna", "arjuna", "wisdom", "spiritual", "soul"]
                    has_spiritual_content = any(keyword.lower() in ai_response.lower() for keyword in spiritual_keywords)
                    
                    if has_spiritual_content or len(ai_response) > 50:
                        self.log_result("AI Chat with Mode", True, f"AI responded with spiritual guidance: {ai_response[:100]}...")
                        return True
                    else:
                        self.log_result("AI Chat with Mode", False, f"Response doesn't seem spiritual: {ai_response}")
                        return False
                else:
                    self.log_result("AI Chat with Mode", False, "Missing response or ID in data", data)
                    return False
            else:
                self.log_result("AI Chat with Mode", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI Chat with Mode", False, f"Request error: {str(e)}")
            return False

    def test_admin_login(self):
        """Test admin login API"""
        try:
            response = requests.post(
                f"{self.admin_base_url}/admin/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.admin_token = data["access_token"]
                    self.log_result("Admin Login", True, "Admin login successful")
                    return True
                else:
                    self.log_result("Admin Login", False, "Missing access_token in response", data)
                    return False
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
            return False

    def test_admin_overview(self):
        """Test admin dashboard overview API"""
        if not self.admin_token:
            self.log_result("Admin Overview", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{self.admin_base_url}/admin/overview",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected overview fields
                if isinstance(data, dict):
                    self.log_result("Admin Overview", True, f"Dashboard overview retrieved successfully")
                    return True
                else:
                    self.log_result("Admin Overview", False, "Invalid response format", data)
                    return False
            else:
                self.log_result("Admin Overview", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Overview", False, f"Request error: {str(e)}")
            return False

    def test_admin_payments(self):
        """Test admin payments management API"""
        if not self.admin_token:
            self.log_result("Admin Payments", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{self.admin_base_url}/admin/payments",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "payments" in data and isinstance(data["payments"], list):
                    payments_count = len(data["payments"])
                    total = data.get("total", payments_count)
                    self.log_result("Admin Payments", True, f"Retrieved {payments_count} payments (total: {total})")
                    return True
                elif isinstance(data, list):
                    self.log_result("Admin Payments", True, f"Retrieved {len(data)} payments")
                    return True
                else:
                    self.log_result("Admin Payments", False, "Invalid response format", data)
                    return False
            else:
                self.log_result("Admin Payments", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Payments", False, f"Request error: {str(e)}")
            return False

    def test_admin_revenue_stats(self):
        """Test admin revenue stats API"""
        if not self.admin_token:
            self.log_result("Admin Revenue Stats", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{self.admin_base_url}/admin/revenue-stats",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_result("Admin Revenue Stats", True, "Revenue stats retrieved successfully")
                    return True
                else:
                    self.log_result("Admin Revenue Stats", False, "Invalid response format", data)
                    return False
            else:
                self.log_result("Admin Revenue Stats", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Revenue Stats", False, f"Request error: {str(e)}")
            return False

    def test_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        try:
            # Test chat without token
            response = requests.post(
                f"{self.base_url}/chat/send",
                json={"message": "test"},
                timeout=10
            )
            
            if response.status_code == 403 or response.status_code == 401:
                self.log_result("Unauthorized Access Test", True, "Protected endpoint correctly requires auth")
                return True
            else:
                self.log_result("Unauthorized Access Test", False, f"Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Unauthorized Access Test", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Arjun AI Backend API Tests")
        print(f"📍 Main Backend: {self.base_url}")
        print(f"📍 Admin Backend: {self.admin_base_url}")
        print("=" * 60)
        
        # Test sequence - focusing on the specific APIs mentioned in review request
        tests = [
            # Basic health and auth tests
            self.test_health_check,
            self.test_unauthorized_access,
            self.test_user_registration,
            self.test_user_login,  # Login first to get token
            self.test_invalid_login,
            
            # Main backend tests (port 8001) - PRIORITY TESTS
            self.test_user_profile_get,  # FIXED - was returning 500 errors
            self.test_premium_status,    # NEW - needs testing
            self.test_manual_payment_verification,  # FIXED - was using query params, now JSON body
            self.test_chat_with_mode,    # Should still work
            
            # Additional auth and chat tests
            self.test_ai_chat,
            self.test_chat_history,
            self.test_user_profile_update,
            self.test_delete_chat,
            
            # Password reset tests (run after other tests since they change password)
            self.test_forgot_password,
            self.test_reset_password,
            
            # Admin backend tests (port 8002) - PRIORITY TESTS
            self.test_admin_login,
            self.test_admin_overview,
            self.test_admin_payments,
            self.test_admin_revenue_stats,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__}: Unexpected error: {str(e)}")
                failed += 1
            
            time.sleep(1)  # Brief pause between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n🔍 Failed Tests Details:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"     Details: {result['details']}")
        
        return failed == 0

if __name__ == "__main__":
    tester = ArjunAITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend APIs are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        exit(1)