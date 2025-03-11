# Code Writing AI Crew

This implementation creates a software development AI crew that can fully implement code projects based on your requirements. The crew includes:

- **Project Manager**: Analyzes requirements and coordinates the development process
- **Software Architect**: Designs the overall architecture and file structure
- **Developer**: Writes the actual code implementation for each file
- **Code Reviewer**: Reviews code quality and suggests improvements

## Key Features

- Automatically analyzes project requirements to determine needed files and components
- Designs a software architecture before implementation
- Writes complete, working code files (Python, JavaScript, HTML, CSS, etc.)
- Reviews each file for quality and suggests improvements
- Saves all generated code to a designated directory
- Creates a comprehensive implementation report

## How to Use

### Running the Code Writing Crew

1. Make sure you have the crewAI package properly installed
2. Ensure Ollama is running with your preferred model (default: llama3:8b)
3. Run the user interface script:
   ```
   python run_code_crew.py
   ```

4. Enter your project requirements when prompted
5. The crew will analyze, design, implement, and review your project
6. All generated code will be saved to the 'generated_code' directory (or your specified directory)

### Example Requirements

The system works best with clear, detailed requirements. Here are some examples:

#### Game Development
```
Create a fully implemented Pong game in Python with the following specifications:
1. Must include complete, runnable Python code
2. Use Pygame for graphics and user interface
3. Features both 1-player mode (against AI) and 2-player mode
4. Include detailed implementation of ball physics and paddle controls
5. Implement scoring system and win conditions
6. Add a simple menu system for game options
7. Include comments throughout the code explaining each section
8. The code must be executable without requiring additional files
```

#### Web Application
```
Create a simple todo list web application with the following features:
1. Frontend using HTML, CSS, and JavaScript
2. Ability to add, edit, delete, and mark tasks as complete
3. Tasks should persist using local storage
4. Include filtering by task status (all, active, completed)
5. Responsive design that works on mobile and desktop
6. Clean, modern UI with good user experience
```

#### Data Analysis Tool
```
Create a Python data analysis tool that:
1. Reads CSV files containing sales data (date, product, amount, customer)
2. Generates summary statistics (mean, median, etc.) for sales amounts
3. Creates visualizations of sales trends over time using matplotlib
4. Identifies top customers and products
5. Outputs results to a formatted HTML report
6. Includes a command-line interface for specifying input files and options
```

## Customization

You can customize the Code Writing Crew in several ways:

### Changing the LLM Model

To use a different Ollama model, modify the `ollama_llm` configuration in `code_writing_crew.py`:

```python
# Configure the LLM with Ollama
ollama_llm = LLM(
    model="ollama/codellama:7b",  # Change to your preferred model
    base_url="http://localhost:11434"
)
```

### Adding Specialized Agents

You can extend the crew by adding specialized agents for specific technologies or aspects of development:

```python
def _create_frontend_specialist(self):
    """Create a frontend specialist agent."""
    return Agent(
        role="Frontend Specialist",
        goal="Create beautiful, responsive user interfaces",
        backstory="You are an expert in frontend development with deep knowledge of HTML, CSS, JavaScript, and UX design principles.",
        llm=self.llm,
        verbose=True
    )
```

## Troubleshooting

If you encounter issues:

1. **Model Limitations**: More complex projects may exceed the capabilities of smaller models. Try using a larger model like `llama3:70b` for better results.

2. **Unclear Output**: If the code quality is poor, try providing more detailed requirements or enabling a higher temperature setting.

3. **Timeout Errors**: For larger projects, the LLM might time out. Try breaking your project into smaller components.

4. **File Detection Issues**: If files aren't properly detected from the architecture design, you can manually specify files by modifying the `extract_files_from_design` method.

## How It Works

1. **Analysis Phase**: The Project Manager analyzes your requirements to determine needed components and approach.

2. **Design Phase**: The Software Architect creates a detailed software architecture design.

3. **Implementation Phase**: The Developer writes code for each identified file.

4. **Review Phase**: The Code Reviewer checks each file for quality and issues.

5. **Report Generation**: A comprehensive report is generated with details about the implementation.

The entire process leverages the strengths of different AI agents working together in specialized roles.
