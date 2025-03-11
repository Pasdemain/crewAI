#!/usr/bin/env python
import os
import sys
from adaptive_crew import AdaptiveCrew

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 80)
    print("                        ADAPTIVE AI CREW INTERFACE")
    print("=" * 80)
    print("\nThis interface allows you to submit prompts to a team of AI agents that will")
    print("adapt their roles, goals, and tasks based on your specific request.\n")
    print("The crew consists of:")
    print("  - A Manager agent who analyzes requirements and coordinates the team")
    print("  - A UI/UX Designer agent who handles interface and user experience")
    print("  - A Developer agent who implements technical solutions\n")
    print("=" * 80)
    print()

def main():
    """Main function to run the adaptive crew interface."""
    print_header()
    
    # Initialize the adaptive crew
    crew = AdaptiveCrew()
    
    # Main interaction loop
    while True:
        # Get user input
        print("Enter your prompt below (or type 'exit' to quit):")
        print("-" * 80)
        user_prompt = input("> ")
        print("-" * 80)
        
        # Check if user wants to exit
        if user_prompt.lower() in ['exit', 'quit', 'q']:
            print("\nThank you for using the Adaptive AI Crew. Goodbye!")
            break
        
        # Skip empty inputs
        if not user_prompt.strip():
            print("Please enter a valid prompt.")
            continue
        
        # Confirm with the user
        print(f"\nYour prompt: {user_prompt}")
        confirm = input("\nSubmit this prompt to the AI crew? (y/n): ")
        
        if confirm.lower() != 'y':
            print("Prompt cancelled. Please try again.")
            continue
        
        print("\nProcessing your request. This may take a few minutes...\n")
        
        try:
            # Process the prompt
            result = crew.process_prompt(user_prompt)
            
            # Display the result
            print("\n" + "=" * 80)
            print("                               RESULT")
            print("=" * 80 + "\n")
            print(result)
            print("\n" + "=" * 80)
            
            # Ask if user wants to save the result
            save = input("\nSave this result to a file? (y/n): ")
            if save.lower() == 'y':
                filename = input("Enter filename (default: result.txt): ").strip() or "result.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Prompt: {user_prompt}\n\n")
                    f.write(result)
                print(f"Result saved to {filename}")
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again with a different prompt or check your configuration.")
        
        # Ask if the user wants to continue
        cont = input("\nSubmit another prompt? (y/n): ")
        if cont.lower() != 'y':
            print("\nThank you for using the Adaptive AI Crew. Goodbye!")
            break
        
        print_header()

if __name__ == "__main__":
    main()
