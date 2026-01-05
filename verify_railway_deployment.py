#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Run this to verify your Railway deployment is working correctly
"""

import asyncio
import aiohttp
import sys
from typing import Dict, List, Tuple
import json


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


async def check_endpoint(session: aiohttp.ClientSession, name: str, url: str, expected_status: int = 200) -> Tuple[bool, str]:
    """Check if an endpoint is accessible and returns expected status"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == expected_status:
                return True, f"Status {response.status}"
            else:
                return False, f"Expected {expected_status}, got {response.status}"
    except asyncio.TimeoutError:
        return False, "Timeout"
    except aiohttp.ClientError as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


async def check_api_endpoint(session: aiohttp.ClientSession, name: str, url: str) -> Tuple[bool, str]:
    """Check API endpoint and parse JSON response"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return True, f"OK - Response: {json.dumps(data)[:50]}..."
                except:
                    return True, "OK (non-JSON response)"
            else:
                return False, f"Status {response.status}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def print_header(text: str):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_result(name: str, success: bool, message: str):
    """Print a test result"""
    icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    status = f"{Colors.GREEN}PASS{Colors.END}" if success else f"{Colors.RED}FAIL{Colors.END}"
    print(f"  {icon} {name:<30} {status:<15} {message}")


def print_summary(total: int, passed: int):
    """Print test summary"""
    failed = total - passed
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Summary:{Colors.END}")
    print(f"  Total Tests:  {total}")
    print(f"  {Colors.GREEN}Passed:{Colors.END}       {passed}")
    print(f"  {Colors.RED}Failed:{Colors.END}       {failed}")
    print(f"  Success Rate: {percentage:.1f}%")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")


async def verify_deployment(backend_url: str, frontend_url: str):
    """Verify Railway deployment"""
    
    print_header("🚂 Railway Deployment Verification")
    
    print(f"{Colors.BOLD}Configuration:{Colors.END}")
    print(f"  Backend URL:  {backend_url}")
    print(f"  Frontend URL: {frontend_url}\n")
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        
        # Backend Tests
        print_header("Backend Service Tests")
        
        tests = [
            ("Health Endpoint", f"{backend_url}/health"),
            ("API Documentation", f"{backend_url}/docs"),
            ("OpenAPI Schema", f"{backend_url}/openapi.json"),
        ]
        
        for name, url in tests:
            success, message = await check_endpoint(session, name, url)
            print_result(name, success, message)
            results.append(success)
        
        # API Endpoints Tests
        print_header("API Endpoints Tests")
        
        api_tests = [
            ("Dashboard API", f"{backend_url}/api/dashboard/stats"),
            ("Vehicles API", f"{backend_url}/api/dashboard/vehicles"),
        ]
        
        for name, url in api_tests:
            success, message = await check_api_endpoint(session, name, url)
            print_result(name, success, message)
            results.append(success)
        
        # Frontend Tests
        print_header("Frontend Service Tests")
        
        frontend_tests = [
            ("Frontend Homepage", frontend_url),
            ("Frontend Health", f"{frontend_url}/health"),
        ]
        
        for name, url in frontend_tests:
            success, message = await check_endpoint(session, name, url)
            print_result(name, success, message)
            results.append(success)
        
        # CORS Test
        print_header("Cross-Origin Tests")
        
        print(f"  {Colors.YELLOW}ℹ{Colors.END} Testing CORS from frontend to backend...")
        try:
            headers = {
                'Origin': frontend_url,
                'Access-Control-Request-Method': 'GET',
            }
            async with session.options(f"{backend_url}/api/dashboard/stats", headers=headers) as response:
                cors_allowed = 'access-control-allow-origin' in response.headers
                if cors_allowed:
                    print_result("CORS Configuration", True, "Origin allowed")
                    results.append(True)
                else:
                    print_result("CORS Configuration", False, "Origin not in CORS policy")
                    results.append(False)
        except Exception as e:
            print_result("CORS Configuration", False, f"Test failed: {str(e)}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print_summary(total, passed)
    
    # Final verdict
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed! Deployment is successful! 🎉{Colors.END}\n")
        return 0
    elif passed >= total * 0.7:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Most tests passed, but some issues detected{Colors.END}")
        print(f"{Colors.YELLOW}  Review failed tests and check configuration{Colors.END}\n")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Multiple tests failed. Deployment needs attention{Colors.END}")
        print(f"{Colors.RED}  Please review the errors and check your Railway configuration{Colors.END}\n")
        return 2


def print_usage():
    """Print usage instructions"""
    print(f"\n{Colors.BOLD}Usage:{Colors.END}")
    print(f"  python verify_railway_deployment.py <backend_url> <frontend_url>")
    print(f"\n{Colors.BOLD}Example:{Colors.END}")
    print(f"  python verify_railway_deployment.py \\")
    print(f"    https://backend.railway.app \\")
    print(f"    https://frontend.railway.app")
    print(f"\n{Colors.BOLD}Note:{Colors.END}")
    print(f"  - URLs should NOT have trailing slashes")
    print(f"  - Use HTTPS URLs (Railway provides SSL automatically)")
    print(f"  - Ensure both services are deployed and running\n")


async def main():
    """Main function"""
    
    # Check arguments
    if len(sys.argv) != 3:
        print(f"{Colors.RED}Error: Invalid arguments{Colors.END}")
        print_usage()
        sys.exit(1)
    
    backend_url = sys.argv[1].rstrip('/')
    frontend_url = sys.argv[2].rstrip('/')
    
    # Validate URLs
    if not backend_url.startswith('http'):
        print(f"{Colors.RED}Error: Backend URL must start with http:// or https://{Colors.END}")
        sys.exit(1)
    
    if not frontend_url.startswith('http'):
        print(f"{Colors.RED}Error: Frontend URL must start with http:// or https://{Colors.END}")
        sys.exit(1)
    
    # Run verification
    try:
        exit_code = await verify_deployment(backend_url, frontend_url)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification cancelled by user{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}\n")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
