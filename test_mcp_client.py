#!/usr/bin/env python3
"""
MCP Client Test Script for FocusForge
Tests the MCP client connection and tool calling functionality
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.mcp.client import MCPSession, get_mcp_client
from app.mcp.config import get_mcp_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClientTester:
    def __init__(self):
        self.results = {}
    
    async def test_connection(self):
        """Test basic MCP connection"""
        try:
            logger.info("Testing MCP connection...")
            async with MCPSession() as mcp:
                connected = mcp.connected
                self.results["connection"] = {
                    "success": connected,
                    "message": "Connected to MCP server" if connected else "Failed to connect"
                }
                logger.info(f"Connection test: {'PASSED' if connected else 'FAILED'}")
                return connected
        except Exception as e:
            self.results["connection"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def test_list_tools(self):
        """Test listing available tools"""
        try:
            logger.info("Testing tool listing...")
            async with MCPSession() as mcp:
                tools = await mcp.list_tools()
                self.results["list_tools"] = {
                    "success": True,
                    "tools_count": len(tools),
                    "tools": [tool.get("name", "unnamed") for tool in tools]
                }
                logger.info(f"Found {len(tools)} tools")
                return True
        except Exception as e:
            self.results["list_tools"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Tool listing failed: {e}")
            return False
    
    async def test_task_breakdown(self):
        """Test task breakdown functionality"""
        try:
            logger.info("Testing task breakdown...")
            async with MCPSession() as mcp:
                result = await mcp.get_task_breakdown(
                    title="Write a Python script",
                    description="Create a script to analyze data",
                    duration_minutes=60
                )
                
                self.results["task_breakdown"] = {
                    "success": result.get("success", False),
                    "has_breakdown": "breakdown" in result,
                    "breakdown_count": len(result.get("breakdown", []))
                }
                logger.info("Task breakdown test completed")
                return True
        except Exception as e:
            self.results["task_breakdown"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Task breakdown test failed: {e}")
            return False
    
    async def test_motivation(self):
        """Test motivation functionality"""
        try:
            logger.info("Testing motivation...")
            async with MCPSession() as mcp:
                result = await mcp.get_motivation(
                    user_id="test_user",
                    current_mood="tired",
                    challenge="feeling overwhelmed"
                )
                
                self.results["motivation"] = {
                    "success": result.get("success", False),
                    "has_motivation": "motivation" in result
                }
                logger.info("Motivation test completed")
                return True
        except Exception as e:
            self.results["motivation"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Motivation test failed: {e}")
            return False
    
    async def test_task_creation(self):
        """Test task creation functionality"""
        try:
            logger.info("Testing task creation...")
            async with MCPSession() as mcp:
                result = await mcp.create_task(
                    title="Test Task",
                    description="A test task for MCP",
                    user_id="test_user",
                    duration_minutes=25
                )
                
                self.results["task_creation"] = {
                    "success": result.get("success", False),
                    "has_task_id": "task_id" in result
                }
                logger.info("Task creation test completed")
                return True
        except Exception as e:
            self.results["task_creation"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Task creation test failed: {e}")
            return False
    
    async def test_mood_logging(self):
        """Test mood logging functionality"""
        try:
            logger.info("Testing mood logging...")
            async with MCPSession() as mcp:
                result = await mcp.log_mood(
                    user_id="test_user",
                    mood="focused",
                    context={"activity": "testing"}
                )
                
                self.results["mood_logging"] = {
                    "success": result.get("success", False),
                    "logged": "logged" in result
                }
                logger.info("Mood logging test completed")
                return True
        except Exception as e:
            self.results["mood_logging"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"Mood logging test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all MCP tests"""
        logger.info("Starting MCP Client Tests...")
        logger.info("=" * 50)
        
        tests = [
            ("Connection", self.test_connection),
            ("List Tools", self.test_list_tools),
            ("Task Breakdown", self.test_task_breakdown),
            ("Motivation", self.test_motivation),
            ("Task Creation", self.test_task_creation),
            ("Mood Logging", self.test_mood_logging)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                status = "PASSED" if result else "FAILED"
                logger.info(f"{test_name}: {status}")
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"{test_name}: FAILED - {e}")
        
        logger.info("=" * 50)
        logger.info(f"Test Results: {passed}/{total} tests passed")
        
        # Print detailed results
        print("\nDetailed Results:")
        print(json.dumps(self.results, indent=2))
        
        return passed == total

async def main():
    """Main function to run MCP tests"""
    logger.info("FocusForge MCP Client Tester")
    logger.info("Testing MCP integration...")
    
    # Show configuration
    try:
        config = get_mcp_config()
        logger.info(f"MCP Server: {config['server']['host']}:{config['server']['port']}")
        logger.info(f"Available tool categories: {list(config['tools'].keys())}")
    except Exception as e:
        logger.error(f"Failed to load MCP config: {e}")
        return False
    
    # Run tests
    tester = MCPClientTester()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("All tests passed! MCP integration is working correctly.")
        return True
    else:
        logger.error("Some tests failed. Check the logs for details.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test runner error: {e}")
        sys.exit(1)
