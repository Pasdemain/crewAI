#!/usr/bin/env python
import os
import sys
import glob
from code_writing_crew import CodeWritingCrew, llama3_llm

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 80)
    print("                 PROJECT CONTINUATION INTERFACE")
    print("=" * 80)
    print("\nThis interface allows you to have the AI crew analyze your existing project")
    print("and continue development based on their analysis.\n")
    print("The crew will:")
    print("  1. Analyze your existing code files")
    print("  2. Review the implementation report")
    print("  3. Implement new features or improve existing ones\n")
    print("=" * 80)
    print()

def read_file(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return f"ERROR: Could not read file - {e}"

def read_report(project_dir):
    """Read the implementation report."""
    report_path = os.path.join(project_dir, "implementation_report.md")
    if os.path.exists(report_path):
        return read_file(report_path)
    return "No implementation report found."

def get_all_project_files(project_dir):
    """Get all project files and their content."""
    files = {}
    
    # Get all files in the directory and subdirectories
    for ext in ['*.py', '*.js', '*.html', '*.css', '*.md']:
        for file_path in glob.glob(os.path.join(project_dir, '**', ext), recursive=True):
            if os.path.isfile(file_path) and 'implementation_report.md' not in file_path:
                rel_path = os.path.relpath(file_path, project_dir)
                content = read_file(file_path)
                files[rel_path] = content
    
    return files

def continue_project(project_dir, new_requirements):
    """Continue an existing project with new requirements."""
    # Create an instance of CodeWritingCrew for the project directory
    crew = CodeWritingCrew(project_dir=project_dir)
    
    # Read the implementation report
    report = read_report(project_dir)
    print(f"Read implementation report: {len(report)} characters")
    
    # Get all project files
    files = get_all_project_files(project_dir)
    print(f"Found {len(files)} files in the project")
    
    # Create a context about the existing project
    project_context = f"""
IMPLEMENTATION REPORT:
{report}

EXISTING FILES:
"""
    # Add file summaries - limit to 500 chars per file to avoid context length issues
    for filename, content in files.items():
        summary = content[:500] + "..." if len(content) > 500 else content
        project_context += f"\n--- {filename} ---\n{summary}\n"
    
    # Create an analysis task to understand the current project
    analysis_task = crew.project_manager.create_task(
        description=f"""
        Analyze this existing project based on:
        
        {project_context}
        
        New requirements to implement:
        {new_requirements}
        
        Provide:
        1. A summary of the existing project's structure and functionality
        2. What has already been implemented
        3. What needs to be implemented based on the new requirements
        4. A plan to continue development
        
        Think step-by-step and be thorough in your analysis.
        """,
        expected_output="A comprehensive analysis of the existing project and plan for continuing development"
    )
    
    # Create a temporary crew for the analysis
    analysis_crew = crew._create_crew(
        agents=[crew.project_manager],
        tasks=[analysis_task]
    )
    
    # Get the analysis result
    print("\n=== ANALYZING EXISTING PROJECT ===\n")
    analysis_result = analysis_crew.kickoff()
    analysis = analysis_result.raw if hasattr(analysis_result, 'raw') else str(analysis_result)
    print(f"\nProject Analysis Completed: {len(analysis)} chars\n")
    
    # Extract files to update/create from the analysis
    files_to_implement = crew.extract_files_from_design(analysis)
    
    # If no specific files were detected, check from the existing project
    if not files_to_implement:
        files_to_implement = list(files.keys())
    
    print(f"\nDetected {len(files_to_implement)} files to update: {', '.join(files_to_implement)}\n")
    
    # Implement/update each file
    implemented_files = {}
    reviews = {}
    
    for filename in files_to_implement:
        print(f"\n=== UPDATING {filename} ===\n")
        existing_files = crew.list_existing_files()
        file_path, code_content = crew.implement_file(
            filename, 
            f"EXISTING PROJECT CONTEXT:\n{project_context}\n\nNEW REQUIREMENTS:\n{new_requirements}",
            analysis, 
            existing_files
        )
        implemented_files[filename] = file_path
        
        # Review the implemented code
        print(f"\n=== REVIEWING {filename} ===\n")
        review = crew.review_code(filename, code_content, new_requirements)
        reviews[filename] = review
    
    # Generate a continuation report
    continuation_report = f"""# Project Continuation Report
Generated on: {crew._get_current_datetime()}

## Original Project Analysis
```
{analysis[:1000]}...
```

## New Requirements
```
{new_requirements}
```

## Updated/Created Files
"""
    
    for filename, filepath in implemented_files.items():
        continuation_report += f"- [{filename}]({os.path.basename(filepath)})\n"
    
    continuation_report += "\n## Code Reviews\n"
    
    for filename, review in reviews.items():
        continuation_report += f"\n### {filename} Review\n"
        continuation_report += review + "\n"
    
    continuation_report += "\n## Next Steps\n"
    continuation_report += "1. Test the updated implementation thoroughly\n"
    continuation_report += "2. Address issues identified in the code reviews\n"
    continuation_report += "3. Consider further enhancements based on the requirements\n"
    
    # Save the continuation report
    report_path = os.path.join(project_dir, "continuation_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(continuation_report)
    
    return {
        "project_dir": project_dir,
        "updated_files": implemented_files,
        "reviews": reviews,
        "report": report_path
    }

def main():
    """Main function to run the project continuation interface."""
    print_header()
    
    # Get the project directory
    default_dir = os.path.join(os.getcwd(), "generated_code")
    if not os.path.exists(default_dir):
        default_dir = os.getcwd()
    
    print("Which project would you like to continue?")
    custom_dir = input(f"(Press Enter for default: {default_dir}): ")
    
    project_dir = custom_dir if custom_dir.strip() else default_dir
    
    if not os.path.exists(project_dir):
        print(f"Error: Directory {project_dir} does not exist.")
        return
    
    # Display existing files
    files = get_all_project_files(project_dir)
    
    if not files:
        print(f"No code files found in {project_dir}")
        return
    
    print(f"\nFound {len(files)} files in the project:")
    for file in sorted(files.keys()):
        print(f"- {file}")
    
    # Get new requirements
    print("\nPlease enter new requirements or features to implement:")
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
        return
    
    # Confirm with the user
    print(f"\nRequirements summary: {len(requirements.split())} words entered.")
    confirm = input("\nSubmit these requirements to continue the project? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    print("\nAnalyzing existing project and continuing development. This may take several minutes...\n")
    
    try:
        # Process the continuation
        result = continue_project(project_dir, requirements)
        
        # Display the result
        print("\n" + "=" * 80)
        print("                   PROJECT CONTINUATION COMPLETED")
        print("=" * 80 + "\n")
        print(f"Project updated in: {result['project_dir']}")
        print("\nUpdated/Created files:")
        for filename, filepath in result["updated_files"].items():
            print(f"- {filename}")
        
        print(f"\nDetailed report saved to: {os.path.basename(result['report'])}")
        
        # Open the project directory
        open_dir = input("\nWould you like to open the project directory? (y/n): ")
        if open_dir.lower() == 'y':
            os.startfile(result['project_dir']) if os.name == 'nt' else os.system(f"xdg-open {result['project_dir']}")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Please try again with different requirements or check your configuration.")

if __name__ == "__main__":
    main()
