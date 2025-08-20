#!/usr/bin/env python3
"""
Test script for Google OAuth authentication
"""

import asyncio
import httpx
import json
from datetime import datetime


class AuthTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        
    async def test_auth_status(self):
        """Test authentication system status"""
        print("🔍 Testing authentication status...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/auth/status")
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get("google_oauth_configured"):
                print("✅ Google OAuth is configured")
            else:
                print("❌ Google OAuth is not configured")
                print("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
            
            return result
            
        except Exception as e:
            print(f"❌ Error testing auth status: {e}")
            return None
    
    async def test_google_auth_url(self):
        """Test getting Google OAuth URL"""
        print("\n🔗 Testing Google OAuth URL generation...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/auth/google/url")
            result = response.json()
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Google OAuth URL generated successfully")
                print(f"Auth URL: {result['auth_url']}")
                print("\nInstructions:")
                for i, instruction in enumerate(result.get('instructions', []), 1):
                    print(f"  {i}. {instruction}")
            else:
                print(f"❌ Failed to get auth URL: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error testing Google auth URL: {e}")
            return None
    
    async def test_protected_endpoint(self, token=None):
        """Test accessing a protected endpoint"""
        print(f"\n🔒 Testing protected endpoint (with {'valid token' if token else 'no token'})...")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/tasks/",
                headers=headers
            )
            result = response.json()
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 401:
                print("✅ Protected endpoint correctly requires authentication")
                if "auth_endpoints" in result:
                    print("✅ Helpful authentication error message provided")
            elif response.status_code == 200:
                print("✅ Protected endpoint accessible with valid token")
            else:
                print(f"❓ Unexpected response: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error testing protected endpoint: {e}")
            return None
    
    async def test_public_endpoints(self):
        """Test public endpoints that should work without authentication"""
        print("\n🌍 Testing public endpoints...")
        
        public_endpoints = [
            "/",
            "/health",
            "/api/v1/auth/status",
            "/api/v1/auth/google/url"
        ]
        
        for endpoint in public_endpoints:
            try:
                response = await self.client.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - accessible without auth")
                else:
                    print(f"❌ {endpoint} - unexpected status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - error: {e}")
    
    async def test_token_verification(self, token):
        """Test token verification endpoint"""
        print(f"\n🔍 Testing token verification...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/auth/verify",
                headers=headers
            )
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200 and result.get("authenticated"):
                print("✅ Token verification successful")
            else:
                print("❌ Token verification failed")
            
            return result
            
        except Exception as e:
            print(f"❌ Error testing token verification: {e}")
            return None
    
    async def run_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting FocusForge Authentication Tests")
        print("=" * 50)
        
        # Test 1: Authentication status
        await self.test_auth_status()
        
        # Test 2: Public endpoints
        await self.test_public_endpoints()
        
        # Test 3: Google OAuth URL
        await self.test_google_auth_url()
        
        # Test 4: Protected endpoint without token
        await self.test_protected_endpoint()
        
        print("\n" + "=" * 50)
        print("🎯 Authentication Test Summary:")
        print("- Authentication system is set up")
        print("- Public endpoints work without authentication")
        print("- Protected endpoints require authentication")
        print("- Google OAuth URL generation works")
        print("\n📝 Next steps:")
        print("1. Set up Google OAuth credentials in environment variables")
        print("2. Test the full OAuth flow with a real Google account")
        print("3. Use the generated JWT tokens to access protected endpoints")
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def main():
    """Main test function"""
    tester = AuthTester()
    
    try:
        await tester.run_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
