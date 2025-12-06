"""
Test script for interruption handling
"""

import asyncio
import logging

from handler import InterruptionHandler

logging.basicConfig(level=logging.INFO)


async def main():
    """Run all test scenarios"""
    
    handler = InterruptionHandler()
    
    print("\n" + "="*70)
    print("TEST 1: Filler words while agent SPEAKING")
    print("="*70)
    
    handler.set_speaking(True)
    test_cases = [
        ("yeah", False),
        ("okay", False),
        ("hmm", False),
        ("uh-huh", False),
        ("right", False),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = handler.should_process(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> process={result} (expected={expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}\n")
    
    print("="*70)
    print("TEST 2: Command words while agent SPEAKING")
    print("="*70)
    
    test_cases = [
        ("wait", True),
        ("stop", True),
        ("no", True),
        ("hold on", True),
        ("but", True),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = handler.should_process(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> process={result} (expected={expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}\n")
    
    print("="*70)
    print("TEST 3: Filler words while agent SILENT")
    print("="*70)
    
    handler.set_speaking(False)
    test_cases = [
        ("yeah", True),
        ("okay", True),
        ("sure", True),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = handler.should_process(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> process={result} (expected={expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}\n")
    
    print("="*70)
    print("TEST 4: Mixed input while agent SPEAKING")
    print("="*70)
    
    handler.set_speaking(True)
    test_cases = [
        ("yeah okay but wait", True),
        ("hmm wait a second", True),
        ("okay no stop", True),
        ("yeah right continue", False),
        ("hmm okay", False),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = handler.should_process(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> process={result} (expected={expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}\n")
    
    print("="*70)
    print("🎉 ALL TESTS COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())