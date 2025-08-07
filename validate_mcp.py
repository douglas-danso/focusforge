#!/usr/bin/env python3
"""
MCP Implementation Validation Script
Checks that all MCP components are properly implemented
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_structure():
    """Validate the MCP directory structure"""
    print("🔍 Checking MCP Implementation Structure...")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Core implementation files
    files_to_check = [
        (backend_dir / "app" / "mcp" / "__init__.py", "MCP Package Init"),
        (backend_dir / "app" / "mcp" / "server.py", "MCP Server Implementation"),
        (backend_dir / "app" / "mcp" / "client.py", "MCP Client Implementation"),
        (backend_dir / "app" / "mcp" / "config.py", "MCP Configuration"),
        (backend_dir / "app" / "api" / "v1" / "endpoints" / "mcp.py", "MCP API Endpoints"),
        (project_root / "start_mcp_server.py", "MCP Server Startup Script"),
        (project_root / "test_mcp_client.py", "MCP Client Test Script"),
        (project_root / "setup_mcp.ps1", "PowerShell Setup Script"),
        (project_root / "MCP_INTEGRATION.md", "MCP Documentation"),
    ]
    
    # Check all files
    all_exist = True
    for filepath, description in files_to_check:
        exists = check_file_exists(filepath, description)
        if not exists:
            all_exist = False
    
    print("\n" + "=" * 60)
    
    # Check if LLM service has been updated
    llm_service_path = backend_dir / "app" / "services" / "llm_service.py"
    if llm_service_path.exists():
        content = llm_service_path.read_text()
        has_mcp_methods = "decompose_task_mcp" in content
        status = "✅" if has_mcp_methods else "❌"
        print(f"{status} LLM Service MCP Integration: MCP methods present")
        all_exist = all_exist and has_mcp_methods
    else:
        print("❌ LLM Service: File not found")
        all_exist = False
    
    # Check if router has been updated
    router_path = backend_dir / "app" / "api" / "v1" / "router.py"
    if router_path.exists():
        content = router_path.read_text()
        has_mcp_router = "mcp.router" in content
        status = "✅" if has_mcp_router else "❌"
        print(f"{status} API Router MCP Integration: MCP router included")
        all_exist = all_exist and has_mcp_router
    else:
        print("❌ API Router: File not found")
        all_exist = False
    
    return all_exist

def check_implementation_completeness():
    """Check key implementation components"""
    print("\n🔧 Checking Implementation Completeness...")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Check MCP server implementation
    server_path = backend_dir / "app" / "mcp" / "server.py"
    if server_path.exists():
        content = server_path.read_text()
        
        checks = [
            ("MCPServer class", "class MCPServer" in content),
            ("Tool registration", "register_tool" in content),
            ("Task breakdown tool", "task_breakdown" in content),
            ("Motivation tool", "motivation_coach" in content),
            ("Async handlers", "async def" in content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} MCP Server - {check_name}")
    
    # Check MCP client implementation
    client_path = backend_dir / "app" / "mcp" / "client.py"
    if client_path.exists():
        content = client_path.read_text()
        
        checks = [
            ("MCPSession class", "class MCPSession" in content),
            ("Async context manager", "__aenter__" in content),
            ("Tool calling", "call_tool" in content),
            ("Task breakdown method", "get_task_breakdown" in content),
            ("Session management", "connected" in content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} MCP Client - {check_name}")

def check_configuration():
    """Check MCP configuration"""
    print("\n⚙️  Checking Configuration...")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    config_path = backend_dir / "app" / "mcp" / "config.py"
    if config_path.exists():
        content = config_path.read_text()
        
        checks = [
            ("MCP config function", "get_mcp_config" in content),
            ("Server configuration", "server" in content),
            ("Tool categories", "tools" in content),
            ("AI agents category", "ai_agents" in content),
            ("Environment variables", "os.environ" in content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} Configuration - {check_name}")

def print_summary(all_components_exist):
    """Print validation summary"""
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_components_exist:
        print("🎉 ALL MCP COMPONENTS IMPLEMENTED SUCCESSFULLY!")
        print("\nYour MCP integration is ready to use:")
        print("1. Start the MCP server: python start_mcp_server.py")
        print("2. Test the implementation: python test_mcp_client.py")
        print("3. Or use PowerShell: .\\setup_mcp.ps1 -Action both")
        print("\n📖 See MCP_INTEGRATION.md for detailed documentation")
    else:
        print("⚠️  SOME COMPONENTS ARE MISSING OR INCOMPLETE")
        print("\nPlease check the items marked with ❌ above")
        print("Refer to the implementation guide for missing components")
    
    print("\n" + "=" * 60)

def main():
    """Main validation function"""
    print("🚀 FocusForge MCP Implementation Validator")
    print("Checking all MCP components and integration...")
    
    # Run all checks
    structure_ok = check_directory_structure()
    check_implementation_completeness()
    check_configuration()
    
    # Print summary
    print_summary(structure_ok)
    
    return structure_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)
