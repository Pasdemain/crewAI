#!/usr/bin/env python
import os
import sys
from code_writing_crew import CodeWritingCrew

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 80)
    print("                     CODE WRITING AI CREW INTERFACE")
    print("=" * 80)
    print("\nThis interface allows you to submit project requirements to a team of AI agents")
    print("that will analyze, design, implement, and review code based on your specifications.\n")
    print("The crew consists of:")
    print("  - A Project Manager who analyzes requirements")
    print("  - A Software Architect who designs the architecture")
    print("  - A Developer who writes the actual code")
    print("  - A Code Reviewer who checks code quality\n")
    print("All code will be saved to the 'generated_code' directory.\n")
    print("=" * 80)
    print()

def get_requirements():
    """Get project requirements from the user."""
    print("Enter your project requirements below.")
    print("Include details about functionality, technologies, features, etc.")
    print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter when finished.")
    print("-" * 80)
    
    requirements = []
    try:
        while True:
            line = input()
            requirements.append(line)
    except EOFError:
        pass
    
    return "\n".join(requirements)

def main():
    """Main function to run the code writing crew interface."""
    print_header()
    
    # Ask for custom project directory
    print("Where should the generated code be saved?")
    default_dir = os.path.join(os.getcwd(), "generated_code")
    custom_dir = input(f"(Press Enter for default: {default_dir}): ")
    
    project_dir = custom_dir if custom_dir.strip() else default_dir
    
    # Initialize the code writing crew
    crew = CodeWritingCrew(project_dir=project_dir)
    
    # Main interaction loop
    while True:
        # Get project requirements
        print("\nPlease enter your project requirements:")
        print("(Press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter when finished)")
        print("-" * 80)
        
        requirements = []
        try:
            while True:
                line = input("> ")
                requirements.append(line)
        except EOFError:
            requirements = "\n".join(requirements)
        
        if not requirements.strip():
            print("No requirements entered. Please try again.")
            continue
        
        # Confirm with the user
        print(f"\nRequirements summary: {len(requirements.split())} words entered.")
        confirm = input("\nSubmit these requirements to the AI crew? (y/n): ")
        
        if confirm.lower() != 'y':
            print("Requirements cancelled. Please try again.")
            continue
        
        print("\nProcessing your requirements. This may take several minutes...\n")
        
        try:
            # Process the requirements
            result = crew.implement_project(requirements)
            
            # Display the result
            print("\n" + "=" * 80)
            print("                         PROJECT COMPLETED")
            print("=" * 80 + "\n")
            print(f"Project implemented in: {result['project_dir']}")
            print("\nImplemented files:")
            for filename, filepath in result["implemented_files"].items():
                print(f"- {filename}")
            
            print(f"\nDetailed report saved to: {os.path.basename(result['report'])}")
            
            # Open the project directory
            open_dir = input("\nWould you like to open the project directory? (y/n): ")
            if open_dir.lower() == 'y':
                os.startfile(result['project_dir']) if os.name == 'nt' else os.system(f"xdg-open {result['project_dir']}")
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again with different requirements or check your configuration.")
        
        # Ask if the user wants to continue
        cont = input("\nCreate another project? (y/n): ")
        if cont.lower() != 'y':
            print("\nThank you for using the Code Writing AI Crew. Goodbye!")
            break
        
        print_header()

if __name__ == "__main__":
    main()
