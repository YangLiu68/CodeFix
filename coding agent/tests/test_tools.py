import sys
import os

# Add project root to path so imports work when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.read_file import read_file
from tools.run_command import run_command
from tools.search_code import search_code
from tools.write_file import write_file


def test_tools():
    print("Testing tools...")
    
    # Test write_file
    print("1. Testing write_file...")
    write_result = write_file("tests/test_output.txt", "Hello from tools test!")
    print(f"Result: {write_result}")
    
    # Test read_file
    print("\n2. Testing read_file...")
    read_result = read_file("tests/test_output.txt")
    print(f"Content: {read_result}")
    
    # Test run_command
    print("\n3. Testing run_command...")
    run_result = run_command("ls tests/")
    print(f"Output: {run_result}")
    
    # Test search_code
    print("\n4. Testing search_code...")
    search_result = search_code("Hello", path="tests/")
    print(f"Results:\n{search_result}")
    
    # Cleanup
    if os.path.exists("tests/test_output.txt"):
        os.remove("tests/test_output.txt")
        print("\nCleanup done.")


if __name__ == "__main__":
    test_tools()
