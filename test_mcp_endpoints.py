#!/usr/bin/env python3
"""
Quick MCP Test Script
Tests MCP endpoints without requiring the full MCP library installation
"""

import asyncio
import aiohttp
import json

async def test_mcp_endpoints():
    """Test MCP endpoints"""
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health check (should include MCP status)
        print("🔍 Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                data = await response.json()
                print(f"✅ Health: {data}")
                
                if "mcp" in data:
                    print(f"   MCP Status: {data['mcp']}")
        except Exception as e:
            print(f"❌ Health test failed: {e}")
        
        # Test 2: MCP Status
        print("\n🔍 Testing MCP status...")
        try:
            async with session.get(f"{base_url}/mcp/status") as response:
                data = await response.json()
                print(f"✅ MCP Status: {data}")
        except Exception as e:
            print(f"❌ MCP status test failed: {e}")
        
        # Test 3: List MCP tools
        print("\n🔍 Testing MCP tools list...")
        try:
            async with session.get(f"{base_url}/mcp/tools") as response:
                data = await response.json()
                print(f"✅ MCP Tools: Found {data.get('total_tools', 0)} tools")
                if data.get("tools_by_category"):
                    for category, tools in data["tools_by_category"].items():
                        print(f"   {category}: {len(tools)} tools")
        except Exception as e:
            print(f"❌ MCP tools test failed: {e}")
        
        # Test 4: Test task breakdown via MCP
        print("\n🔍 Testing MCP task breakdown...")
        try:
            task_data = {
                "title": "Write documentation",
                "description": "Create comprehensive API documentation",
                "duration_minutes": 60
            }
            
            async with session.post(
                f"{base_url}/mcp/agents/task-breakdown-mcp",
                json=task_data
            ) as response:
                data = await response.json()
                print(f"✅ Task Breakdown: {data}")
        except Exception as e:
            print(f"❌ Task breakdown test failed: {e}")
        
        # Test 5: Test motivation via MCP
        print("\n🔍 Testing MCP motivation...")
        try:
            motivation_data = {
                "user_id": "test_user",
                "current_mood": "tired",
                "challenge": "feeling overwhelmed"
            }
            
            async with session.post(
                f"{base_url}/mcp/agents/motivation-mcp",
                json=motivation_data
            ) as response:
                data = await response.json()
                print(f"✅ Motivation: {data}")
        except Exception as e:
            print(f"❌ Motivation test failed: {e}")

async def main():
    print("🚀 FocusForge MCP Endpoint Tester")
    print("Testing MCP integration endpoints...")
    print("=" * 50)
    
    await test_mcp_endpoints()
    
    print("\n" + "=" * 50)
    print("✨ MCP endpoint testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
