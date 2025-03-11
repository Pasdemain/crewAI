# Adaptive AI Crew

This implementation creates a dynamic AI crew that adapts to user prompts, featuring:

- **Manager Agent**: Analyzes requirements and coordinates the team
- **UI/UX Designer Agent**: Handles interface and user experience design
- **Developer Agent**: Implements technical solutions

The system automatically adapts agent roles, goals, and tasks based on your specific request, creating a flexible AI team that can handle various types of projects.

## How It Works

1. The system uses an initial prompt analysis to understand your request
2. Based on the analysis, it reconfigures each agent with tailored:
   - Role definitions
   - Specific goals
   - Relevant backstories
   - Custom tasks
3. The reconfigured agents work together to create a comprehensive solution

## Getting Started

### Prerequisites

Ensure you have:
- crewAI properly installed (see main repository README)
- Ollama running with at least one of these models:
  - llama3:8b
  - codellama:7b
  - phi3:mini

### Running the Adaptive Crew

1. Navigate to your crewAI repository directory:
   ```
   cd C:\Users\RocherT\Documents\Python\AICrew\crewAI
   ```

2. Run the user-friendly interface:
   ```
   python run_adaptive_crew.py
   ```

3. Enter your prompt when prompted. For example:
   ```
   Create a mobile app that helps people track their daily water intake and reminds them to stay hydrated
   ```

4. The system will analyze your prompt, configure the appropriate agents, and execute the tasks to generate a comprehensive solution.

## Example Prompts

Try these example prompts to see how the adaptive crew responds:

- **Web Application**: "Design a website that showcases local artists and allows them to sell their artwork directly to customers"
- **Mobile App**: "Create a fitness tracking app that gamifies workout routines and connects users with personal trainers"
- **Enterprise Software**: "Develop an inventory management system for a small retail business that integrates with their point-of-sale system"
- **Data Dashboard**: "Build a dashboard that visualizes energy consumption patterns in a smart home environment"

## Advanced Usage

### Customizing the LLM

You can modify the LLM used by changing the model in `adaptive_crew.py`:

```python
ollama_llm = LLM(
    model="ollama/codellama:7b",  # Change to your preferred model
    base_url="http://localhost:11434"
)
```

### Adding Additional Agents

The system is designed to be extensible. You can add more specialized agents by modifying the `AdaptiveCrew` class in `adaptive_crew.py`.

## Troubleshooting

If you encounter issues:

1. Ensure Ollama is running in the background
2. Verify that you have the correct model installed (`ollama list`)
3. Check that your prompt is clear and specific enough for the agents to understand

## Understanding the Output

The output will typically include:
- Analysis of your requirements
- Design considerations from the UI/UX agent
- Technical implementation details from the developer agent
- A coordinated plan outlining how the solution should be built

You can save this output to a file for further reference.
