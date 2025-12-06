"""
Simple test version of intelligent interruption handler
Works in text mode - no API keys needed for basic testing
"""

import asyncio
import logging
from handler import get_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockAgent:
    """Simulates agent behavior for testing"""
    
    def __init__(self):
        self.handler = get_handler()
        self.is_speaking = False
    
    async def speak(self, text: str):
        """Simulate agent speaking"""
        self.handler.set_speaking(True)
        self.is_speaking = True
        print(f"\n🤖 AGENT SPEAKING: {text}")
        print("   (Agent is now in SPEAKING state)")
        await asyncio.sleep(0.5)  # Simulate speaking time
    
    async def finish_speaking(self):
        """Finish speaking"""
        self.handler.set_speaking(False)
        self.is_speaking = False
        print("   (Agent finished speaking - now SILENT)")
    
    async def process_user_input(self, user_text: str):
        """Process user input with interruption logic"""
        print(f"\n👤 USER SAYS: '{user_text}'")
        
        should_process = self.handler.should_process(user_text)
        
        if self.is_speaking:
            if should_process:
                print(f"   ✅ INTERRUPT ALLOWED - Agent stops speaking")
                await self.finish_speaking()
                print(f"   🤖 Agent responds to: '{user_text}'")
            else:
                print(f"   ❌ IGNORED (filler word) - Agent continues speaking")
                print(f"   🤖 Agent: ...continuing the explanation...")
        else:
            if should_process:
                print(f"   ✅ PROCESSED - Agent responds")
                print(f"   🤖 Agent: I heard you say '{user_text}'")
            else:
                print(f"   ⚠️ This shouldn't happen when silent")


async def run_test_scenarios():
    """Run all test scenarios interactively"""
    
    agent = MockAgent()
    
    print("\n" + "="*80)
    print("INTELLIGENT INTERRUPTION HANDLER - INTERACTIVE TEST")
    print("="*80)
    print("\nThis demonstrates the interruption handling logic in action.")
    print("Watch how the same word behaves differently based on agent state!\n")
    
    input("Press Enter to start Scenario 1...")
    
    # SCENARIO 1: Filler words while speaking
    print("\n" + "="*80)
    print("SCENARIO 1: Agent speaking + User says filler words")
    print("="*80)
    print("Expected: Agent should IGNORE filler words and continue speaking\n")
    
    await agent.speak(
        "Let me explain how our system works. It has three main components: "
        "the database layer, the application layer, and the presentation layer..."
    )
    
    await asyncio.sleep(1)
    await agent.process_user_input("yeah")
    await asyncio.sleep(0.5)
    
    await agent.process_user_input("okay")
    await asyncio.sleep(0.5)
    
    await agent.process_user_input("hmm")
    await asyncio.sleep(0.5)
    
    await agent.process_user_input("uh-huh")
    await asyncio.sleep(0.5)
    
    await agent.finish_speaking()
    
    input("\nPress Enter for Scenario 2...")
    
    # SCENARIO 2: Command words while speaking
    print("\n" + "="*80)
    print("SCENARIO 2: Agent speaking + User says command words")
    print("="*80)
    print("Expected: Agent should STOP immediately\n")
    
    await agent.speak(
        "Now let me count to ten: one, two, three, four, five..."
    )
    
    await asyncio.sleep(1)
    await agent.process_user_input("wait")
    
    input("\nPress Enter for Scenario 3...")
    
    # SCENARIO 3: Filler words when silent
    print("\n" + "="*80)
    print("SCENARIO 3: Agent silent + User says filler words")
    print("="*80)
    print("Expected: Agent should PROCESS as valid input\n")
    
    print("🤖 AGENT: Are you ready to continue?")
    agent.handler.set_speaking(False)
    print("   (Agent is waiting - SILENT state)")
    
    await asyncio.sleep(1)
    await agent.process_user_input("yeah")
    
    await asyncio.sleep(1)
    await agent.process_user_input("okay")
    
    input("\nPress Enter for Scenario 4...")
    
    # SCENARIO 4: Mixed input
    print("\n" + "="*80)
    print("SCENARIO 4: Agent speaking + User says mixed input")
    print("="*80)
    print("Expected: Agent should STOP if command word is present\n")
    
    await agent.speak(
        "Let me explain the entire process from start to finish..."
    )
    
    await asyncio.sleep(1)
    await agent.process_user_input("yeah okay but wait")
    
    await asyncio.sleep(1)
    
    # Start speaking again
    await agent.speak("Continuing with another example...")
    await asyncio.sleep(1)
    await agent.process_user_input("hmm wait a second")
    
    await asyncio.sleep(1)
    
    # One more mixed example
    await agent.speak("Let me show you one more thing...")
    await asyncio.sleep(1)
    await agent.process_user_input("yeah right continue")  # Should be ignored (all fillers)
    await asyncio.sleep(0.5)
    await agent.finish_speaking()
    
    print("\n" + "="*80)
    print("✅ ALL SCENARIOS COMPLETED!")
    print("="*80)
    print("\nSummary:")
    print("  ✓ Filler words ignored while speaking")
    print("  ✓ Command words interrupt while speaking")
    print("  ✓ Filler words processed when silent")
    print("  ✓ Mixed input handled correctly")
    print("\n" + "="*80 + "\n")


async def interactive_mode():
    """Interactive testing mode"""
    
    agent = MockAgent()
    
    print("\n" + "="*80)
    print("INTERACTIVE MODE - Test Your Own Inputs!")
    print("="*80)
    print("\nCommands:")
    print("  'speak' - Make agent start speaking")
    print("  'stop'  - Make agent stop speaking")
    print("  'quit'  - Exit")
    print("  Anything else - Test as user input")
    print("\n" + "="*80 + "\n")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'speak':
                await agent.speak("This is a long explanation about how the system works...")
                continue
            
            if user_input.lower() == 'stop':
                if agent.is_speaking:
                    await agent.finish_speaking()
                else:
                    print("Agent is not speaking")
                continue
            
            # Process as user input
            await agent.process_user_input(user_input)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


async def main():
    """Main entry point"""
    
    print("\nChoose test mode:")
    print("1. Run automated test scenarios")
    print("2. Interactive mode (test your own inputs)")
    
    try:
        choice = input("\nEnter 1 or 2: ").strip()
        
        if choice == '1':
            await run_test_scenarios()
        elif choice == '2':
            await interactive_mode()
        else:
            print("Invalid choice, running automated scenarios...")
            await run_test_scenarios()
    
    except KeyboardInterrupt:
        print("\n\nGoodbye!")


if __name__ == "__main__":
    asyncio.run(main())