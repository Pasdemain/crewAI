from crewai import Agent, Crew, Task, Process
from crewai import LLM
import re
import os
import datetime
from typing import List, Dict, Any

# Configure the specialized LLMs for each agent role
llama3_llm = LLM(
    model="ollama/llama3:8b",  # General purpose model for management
    base_url="http://localhost:11434"
)

phi3_llm = LLM(
    model="ollama/phi3:mini",  # Good for UI/UX and design
    base_url="http://localhost:11434"
)

codellama_llm = LLM(
    model="ollama/codellama:7b",  # Specialized for coding tasks
    base_url="http://localhost:11434"
)

class CodeWritingCrew:
    """A dynamic crew that can write code files and track development progress."""
    
    def __init__(self, project_dir=None):
        """Initialize with project directory."""
        # Set up project directory
        self.project_dir = project_dir if project_dir else os.path.join(os.getcwd(), "generated_code")
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Initialize code tracking
        self.code_files = {}  # Store filenames and their content
        
        # Initialize agents with specialized models
        self.project_manager = self._create_project_manager()
        self.architect = self._create_architect()
        self.developer = self._create_developer()
        self.code_reviewer = self._create_code_reviewer()
        
        self.agents = [self.project_manager, self.architect, self.developer, self.code_reviewer]
        self.tasks = []
        
    def _create_project_manager(self):
        """Create the project manager agent with llama3."""
        return Agent(
            role="Project Manager",
            goal="Coordinate the software development process and ensure clear requirements",
            backstory="You are an experienced project manager who excels at breaking down complex requirements into clear, actionable tasks. You help the team stay organized and focused.",
            llm=llama3_llm,  # Using llama3 for management tasks
            verbose=True
        )
    
    def _create_architect(self):
        """Create the software architect agent with llama3."""
        return Agent(
            role="Software Architect",
            goal="Design clean, maintainable software architecture",
            backstory="You are a skilled software architect with years of experience designing robust systems. You can identify the right patterns and structures for any project.",
            llm=llama3_llm,  # Using llama3 for architecture design
            verbose=True
        )
    
    def _create_developer(self):
        """Create the developer agent with CodeLlama."""
        return Agent(
            role="Developer",
            goal="Implement high-quality, working code",
            backstory="You are a talented developer who writes clean, efficient, and well-documented code. You have expertise in multiple programming languages and frameworks.",
            llm=codellama_llm,  # Using CodeLlama for coding tasks
            verbose=True
        )
    
    def _create_code_reviewer(self):
        """Create the code reviewer agent with CodeLlama."""
        return Agent(
            role="Code Reviewer",
            goal="Ensure code quality, identify bugs, and suggest improvements",
            backstory="You are a detail-oriented code reviewer with a keen eye for bugs, inefficiencies, and improvements. You help maintain high code quality standards.",
            llm=codellama_llm,  # Using CodeLlama for code review
            verbose=True
        )
    
    def save_code_to_file(self, filename, code_content):
        """Save generated code to a file."""
        # Create the full file path
        file_path = os.path.join(self.project_dir, filename)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the code to the file
        with open(file_path, 'w') as file:
            file.write(code_content)
        
        # Store the code in the tracking dictionary
        self.code_files[filename] = code_content
        
        return file_path
    
    def read_code_from_file(self, filename):
        """Read code from a file."""
        file_path = os.path.join(self.project_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        else:
            return None
    
    def list_existing_files(self):
        """List all existing code files in the project directory."""
        if os.path.exists(self.project_dir):
            return [f for f in os.listdir(self.project_dir) if os.path.isfile(os.path.join(self.project_dir, f))]
        return []
    
    def analyze_requirements(self, requirements):
        """Analyze project requirements to identify needed files and structures."""
        analysis_task = Task(
            description=f"""
            Analyze the following software requirements:
            
            {requirements}
            
            Identify:
            1. The necessary files that will need to be created
            2. The main components and classes needed
            3. Any dependencies or libraries required
            4. A general development approach
            
            Think step-by-step and be thorough in your analysis.
            """,
            agent=self.project_manager,
            expected_output="A comprehensive analysis of the requirements with identified files, components, and development approach."
        )
        
        # Create a temporary crew for the analysis
        analysis_crew = Crew(
            agents=[self.project_manager],
            tasks=[analysis_task],
            verbose=True
        )
        
        # Get the analysis result
        result = analysis_crew.kickoff()
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)
    
    def design_architecture(self, requirements, analysis):
        """Design the software architecture."""
        design_task = Task(
            description=f"""
            Based on the following requirements and analysis:
            
            Requirements:
            {requirements}
            
            Analysis:
            {analysis}
            
            Create a detailed software architecture design, including:
            1. File structure and organization
            2. Class diagrams or descriptions
            3. Major functions and their purposes
            4. Data flow between components
            
            Think step-by-step and be thorough in your design.
            """,
            agent=self.architect,
            expected_output="A comprehensive software architecture design with file structure, class diagrams, and component relationships."
        )
        
        # Create a temporary crew for the design
        design_crew = Crew(
            agents=[self.architect],
            tasks=[design_task],
            verbose=True
        )
        
        # Get the design result
        result = design_crew.kickoff()
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)
    
    def extract_files_from_design(self, design):
        """Extract file names and descriptions from architecture design."""
        # Use regex to find file mentions in the design
        file_pattern = r'(?:filename|file):?\s*["\']?([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)["\']?'
        files = re.findall(file_pattern, design, re.IGNORECASE)
        
        # If no files found with the pattern, try a simpler approach
        if not files:
            py_files = re.findall(r'([a-zA-Z0-9_\-./]+\.py)', design, re.IGNORECASE)
            js_files = re.findall(r'([a-zA-Z0-9_\-./]+\.js)', design, re.IGNORECASE)
            html_files = re.findall(r'([a-zA-Z0-9_\-./]+\.html)', design, re.IGNORECASE)
            css_files = re.findall(r'([a-zA-Z0-9_\-./]+\.css)', design, re.IGNORECASE)
            files = py_files + js_files + html_files + css_files
        
        return list(set(files))  # Remove duplicates
    
    def implement_file(self, filename, requirements, design, existing_files):
        """Implement a specific file."""
        # Read existing code if the file already exists
        existing_code = self.read_code_from_file(filename) if filename in existing_files else "File does not exist yet."
        
        # Create a context about other files
        other_files_context = "Existing project files:\n"
        for f in existing_files:
            if f != filename:
                other_files_context += f"- {f}\n"
                # Optionally include file summaries here
                file_content = self.read_code_from_file(f)
                if file_content:
                    summary = file_content[:500] + "..." if len(file_content) > 500 else file_content
                    other_files_context += f"  Summary: {summary}\n\n"
        
        # Adjust context format based on file type
        if filename.endswith('.py'):
            language_note = "This is a Python file. Use proper Python syntax, PEP 8 style, and include docstrings."
        elif filename.endswith('.js'):
            language_note = "This is a JavaScript file. Use modern ES6+ syntax where appropriate."
        elif filename.endswith('.html'):
            language_note = "This is an HTML file. Use proper HTML5 structure and semantic tags."
        elif filename.endswith('.css'):
            language_note = "This is a CSS file. Use clean, organized styles with appropriate comments."
        else:
            language_note = f"This is a {filename.split('.')[-1]} file. Use proper syntax and conventions for this language."
        
        implementation_task = Task(
            description=f"""
            Implement the file '{filename}' based on the following requirements, design, and context:
            
            Requirements:
            {requirements}
            
            Architecture Design:
            {design}
            
            {other_files_context}
            
            Current state of this file:
            {existing_code}
            
            {language_note}
            
            Write complete, working, well-documented code for this file. The code should be:
            1. Fully functional without errors
            2. Well-commented to explain each section
            3. Following best practices for the language
            4. Compatible with the overall architecture
            
            Write ONLY the code content, nothing else. No explanations outside of code comments.
            """,
            agent=self.developer,
            expected_output=f"Complete, working code for the {filename} file that meets all requirements."
        )
        
        # Create a temporary crew for the implementation
        implementation_crew = Crew(
            agents=[self.developer],
            tasks=[implementation_task],
            verbose=True
        )
        
        # Get the implementation result
        result = implementation_crew.kickoff()
        code_content = result.raw if hasattr(result, 'raw') else str(result)
        
        # Clean up code content (remove markdown code blocks if present)
        code_content = re.sub(r'```\w*\n', '', code_content)
        code_content = re.sub(r'```', '', code_content)
        
        # Save the implemented code to file
        file_path = self.save_code_to_file(filename, code_content)
        return file_path, code_content
    
    def design_ui(self, requirements, analysis):
        """Design the user interface using Phi3 model."""
        # Create a UI/UX designer agent using Phi3
        ui_ux_designer = Agent(
            role="UI/UX Designer",
            goal="Design intuitive, user-friendly interfaces that meet user requirements",
            backstory="You are a talented UI/UX designer with a keen eye for aesthetics and usability. You create designs that balance visual appeal with functionality.",
            llm=phi3_llm,  # Using Phi3 for UI/UX design
            verbose=True
        )
        
        design_task = Task(
            description=f"""
            Based on the following requirements and analysis:
            
            Requirements:
            {requirements}
            
            Analysis:
            {analysis}
            
            Design the user interface for this application, including:
            1. Layout and screen designs
            2. Color scheme and typography 
            3. User flow and interaction patterns
            4. Visual elements and components
            
            Be specific about dimensions, colors (with hex codes), fonts, and layout.
            Think step-by-step and be thorough in your design.
            """,
            agent=ui_ux_designer,
            expected_output="A comprehensive UI/UX design with layout, visual elements, and interaction patterns."
        )
        
        # Create a temporary crew for the design
        design_crew = Crew(
            agents=[ui_ux_designer],
            tasks=[design_task],
            verbose=True
        )
        
        # Get the design result
        result = design_crew.kickoff()
        ui_design = result.raw if hasattr(result, 'raw') else str(result)
        
        # Save the UI design to a file
        self.save_code_to_file("ui_design.md", ui_design)
        
        return ui_design
    
    def review_code(self, filename, code_content, requirements):
        """Review implemented code for a file."""
        review_task = Task(
            description=f"""
            Review the following code for '{filename}':
            
            ```
            {code_content}
            ```
            
            Considering these requirements:
            {requirements}
            
            Evaluate the code for:
            1. Functionality - Does it work as intended?
            2. Code quality - Is it well-structured and readable?
            3. Documentation - Is it well-commented?
            4. Edge cases - Are potential issues handled?
            5. Improvements - What could be better?
            
            Provide specific examples and line numbers for any issues found.
            """,
            agent=self.code_reviewer,
            expected_output=f"A thorough code review for {filename} with identified issues and recommendations."
        )
        
        # Create a temporary crew for the review
        review_crew = Crew(
            agents=[self.code_reviewer],
            tasks=[review_task],
            verbose=True
        )
        
        # Get the review result
        result = review_crew.kickoff()
        review_content = result.raw if hasattr(result, 'raw') else str(result)
        
        return review_content
    
    def implement_project(self, requirements):
        """Implement a complete software project based on requirements."""
        print(f"Starting project implementation for: {requirements[:100]}...")
        
        # Step 1: Analyze the requirements
        print("\n=== ANALYZING REQUIREMENTS ===\n")
        analysis = self.analyze_requirements(requirements)
        print(f"\nRequirements Analysis Completed: {len(analysis)} chars\n")
        
        # Step 2: Design the architecture
        print("\n=== DESIGNING ARCHITECTURE ===\n")
        design = self.design_architecture(requirements, analysis)
        print(f"\nArchitecture Design Completed: {len(design)} chars\n")
        
        # Step 3: Design the UI (if applicable)
        if "ui" in requirements.lower() or "interface" in requirements.lower() or "design" in requirements.lower():
            print("\n=== DESIGNING USER INTERFACE ===\n")
            ui_design = self.design_ui(requirements, analysis)
            print(f"\nUI Design Completed: {len(ui_design)} chars\n")
        else:
            ui_design = "No UI design required for this project."
        
        # Step 4: Extract files from design
        files_to_implement = self.extract_files_from_design(design)
        if not files_to_implement:
            # Fallback if no files were detected
            if "pygame" in requirements.lower():
                files_to_implement = ["main.py", "game.py", "menu.py", "settings.py"]
            elif "web" in requirements.lower() or "html" in requirements.lower():
                files_to_implement = ["index.html", "style.css", "script.js"]
            else:
                files_to_implement = ["main.py", "utils.py"]
        
        print(f"\nDetected {len(files_to_implement)} files to implement: {', '.join(files_to_implement)}\n")
        
        # Step 5: Implement each file
        implemented_files = {}
        reviews = {}
        
        for filename in files_to_implement:
            print(f"\n=== IMPLEMENTING {filename} ===\n")
            existing_files = self.list_existing_files()
            file_path, code_content = self.implement_file(filename, requirements, design, existing_files)
            implemented_files[filename] = file_path
            
            # Step 6: Review the implemented code
            print(f"\n=== REVIEWING {filename} ===\n")
            review = self.review_code(filename, code_content, requirements)
            reviews[filename] = review
        
        # Step 7: Generate a final report
        report = self._generate_report(requirements, analysis, design, ui_design, implemented_files, reviews)
        report_path = os.path.join(self.project_dir, "implementation_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        return {
            "project_dir": self.project_dir,
            "implemented_files": implemented_files,
            "reviews": reviews,
            "report": report_path
        }
    
    def _generate_report(self, requirements, analysis, design, ui_design, implemented_files, reviews):
        """Generate a final implementation report."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Project Implementation Report
Generated on: {now}

## Project Requirements
```
{requirements[:500]}...
```

## Implementation Analysis
```
{analysis[:500]}...
```

## Architecture Design
```
{design[:500]}...
```

## UI/UX Design
```
{ui_design[:500]}...
```

## Implemented Files
"""
        
        for filename, filepath in implemented_files.items():
            report += f"- [{filename}]({os.path.basename(filepath)})\n"
        
        report += "\n## Code Reviews\n"
        
        for filename, review in reviews.items():
            report += f"\n### {filename} Review\n"
            report += review + "\n"
        
        report += "\n## Next Steps\n"
        report += "1. Test the implementation thoroughly\n"
        report += "2. Address issues identified in the code reviews\n"
        report += "3. Consider adding additional features or optimizations\n"
        
        return report

# Example usage
if __name__ == "__main__":
    code_crew = CodeWritingCrew()
    
    # Example requirements
    requirements = """
    Create a simple calculator application in Python that can:
    1. Perform basic operations (add, subtract, multiply, divide)
    2. Have a simple GUI using tkinter
    3. Store calculation history
    4. Allow users to clear the history
    """
    
    result = code_crew.implement_project(requirements)
    
    print(f"\nProject implemented in: {result['project_dir']}")
    print("Implemented files:")
    for filename, filepath in result["implemented_files"].items():
        print(f"- {filename}: {filepath}")
