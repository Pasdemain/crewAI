from crewai import Agent, Crew, Task, Process
from crewai import LLM
import re
from typing import List, Dict, Any

# Configure the LLM with Ollama
ollama_llm = LLM(
    model="ollama/llama3:8b",  # You can change to other models as needed
    base_url="http://localhost:11434"
)

class AdaptiveCrew:
    """A dynamic crew that adapts to different prompts by adjusting agent roles and tasks."""
    
    def __init__(self, llm=None):
        """Initialize with a specific LLM or use the default Ollama."""
        self.llm = llm if llm else ollama_llm
        
        # Initialize with default agents and tasks
        self.manager = self._create_manager()
        self.ui_ux = self._create_ui_ux()
        self.developer = self._create_developer()
        
        self.agents = [self.manager, self.ui_ux, self.developer]
        self.tasks = []
        
    def _create_manager(self, role=None, goal=None, backstory=None):
        """Create the manager agent with default or custom attributes."""
        return Agent(
            role=role or "Project Manager",
            goal=goal or "Understand user requirements and coordinate the team to deliver the best solution",
            backstory=backstory or "You are an experienced project manager who excels at breaking down complex requirements into clear, actionable tasks. You're skilled at understanding user needs and coordinating team efforts.",
            llm=self.llm,
            verbose=True
        )
    
    def _create_ui_ux(self, role=None, goal=None, backstory=None):
        """Create the UI/UX agent with default or custom attributes."""
        return Agent(
            role=role or "UI/UX Designer",
            goal=goal or "Design intuitive, user-friendly interfaces that meet user requirements and provide excellent user experiences",
            backstory=backstory or "You are a talented UI/UX designer with a keen eye for aesthetics and usability. You've designed successful interfaces for various applications and understand how to balance visual appeal with functionality.",
            llm=self.llm,
            verbose=True
        )
    
    def _create_developer(self, role=None, goal=None, backstory=None):
        """Create the developer agent with default or custom attributes."""
        return Agent(
            role=role or "Software Developer",
            goal=goal or "Implement robust, efficient, and maintainable code that fulfills the requirements",
            backstory=backstory or "You are a skilled software developer with expertise in multiple programming languages and frameworks. You write clean, efficient code and are adept at troubleshooting and problem-solving.",
            llm=self.llm,
            verbose=True
        )
    
    def analyze_prompt(self, user_prompt):
        """Analyze the user prompt to determine the appropriate agent configuration."""
        analysis_task = Task(
            description=f"""
            Analyze the following user prompt and suggest the best configuration for our project team:
            
            USER PROMPT: "{user_prompt}"
            
            For each agent (Manager, UI/UX Designer, Developer), suggest:
            1. An appropriate role title
            2. A specific goal related to this prompt
            3. A relevant backstory
            
            Also provide a list of 2-3 tasks for each agent that would be needed to fulfill this prompt.
            
            Format your response strictly as follows:
            MANAGER:
            Role: [role]
            Goal: [goal]
            Backstory: [backstory]
            Tasks:
            - [task1]
            - [task2]
            
            UI_UX:
            Role: [role]
            Goal: [goal]
            Backstory: [backstory]
            Tasks:
            - [task1]
            - [task2]
            
            DEVELOPER:
            Role: [role]
            Goal: [goal]
            Backstory: [backstory]
            Tasks:
            - [task1]
            - [task2]
            """,
            agent=self.manager,
            expected_output="A structured configuration for the three agents with specific roles, goals, backstories, and tasks tailored to the user prompt."
        )
        
        # Create a temporary crew just for analysis
        analysis_crew = Crew(
            agents=[self.manager],
            tasks=[analysis_task],
            verbose=True
        )
        
        # Get the analysis result
        result = analysis_crew.kickoff()
        return result
    
    def parse_analysis(self, analysis):
        """Parse the analysis result to extract agent configurations and tasks."""
        # Extract sections for each agent
        manager_section = re.search(r'MANAGER:(.*?)(?=UI_UX:|$)', analysis, re.DOTALL)
        ui_ux_section = re.search(r'UI_UX:(.*?)(?=DEVELOPER:|$)', analysis, re.DOTALL)
        developer_section = re.search(r'DEVELOPER:(.*?)$', analysis, re.DOTALL)
        
        # Parse each section
        manager_config = self._parse_agent_section(manager_section.group(1) if manager_section else "")
        ui_ux_config = self._parse_agent_section(ui_ux_section.group(1) if ui_ux_section else "")
        developer_config = self._parse_agent_section(developer_section.group(1) if developer_section else "")
        
        return {
            "manager": manager_config,
            "ui_ux": ui_ux_config,
            "developer": developer_config
        }
    
    def _parse_agent_section(self, section):
        """Parse a single agent section to extract role, goal, backstory, and tasks."""
        role = re.search(r'Role:(.*?)(?=Goal:|$)', section, re.DOTALL)
        goal = re.search(r'Goal:(.*?)(?=Backstory:|$)', section, re.DOTALL)
        backstory = re.search(r'Backstory:(.*?)(?=Tasks:|$)', section, re.DOTALL)
        tasks = re.findall(r'- (.*?)$', section, re.MULTILINE)
        
        return {
            "role": role.group(1).strip() if role else "",
            "goal": goal.group(1).strip() if goal else "",
            "backstory": backstory.group(1).strip() if backstory else "",
            "tasks": [task.strip() for task in tasks]
        }
    
    def configure_from_analysis(self, agent_configs):
        """Configure agents and tasks based on the parsed analysis."""
        # Reconfigure agents
        self.manager = self._create_manager(
            role=agent_configs["manager"]["role"] or None,
            goal=agent_configs["manager"]["goal"] or None,
            backstory=agent_configs["manager"]["backstory"] or None
        )
        
        self.ui_ux = self._create_ui_ux(
            role=agent_configs["ui_ux"]["role"] or None,
            goal=agent_configs["ui_ux"]["goal"] or None,
            backstory=agent_configs["ui_ux"]["backstory"] or None
        )
        
        self.developer = self._create_developer(
            role=agent_configs["developer"]["role"] or None,
            goal=agent_configs["developer"]["goal"] or None,
            backstory=agent_configs["developer"]["backstory"] or None
        )
        
        self.agents = [self.manager, self.ui_ux, self.developer]
        
        # Create tasks
        self.tasks = []
        
        # Manager tasks
        for i, task_desc in enumerate(agent_configs["manager"]["tasks"]):
            self.tasks.append(Task(
                description=task_desc,
                agent=self.manager,
                expected_output=f"Detailed analysis and plan for {task_desc.lower()}"
            ))
        
        # UI/UX tasks
        for i, task_desc in enumerate(agent_configs["ui_ux"]["tasks"]):
            self.tasks.append(Task(
                description=task_desc,
                agent=self.ui_ux,
                expected_output=f"Comprehensive design and user experience solution for {task_desc.lower()}"
            ))
        
        # Developer tasks
        for i, task_desc in enumerate(agent_configs["developer"]["tasks"]):
            self.tasks.append(Task(
                description=task_desc,
                agent=self.developer,
                expected_output=f"Implementation plan and code architecture for {task_desc.lower()}"
            ))
    
    def process_prompt(self, user_prompt):
        """Process a user prompt by analyzing it and reconfiguring the crew accordingly."""
        print(f"Analyzing prompt: {user_prompt}")
        
        # Analyze the prompt
        analysis = self.analyze_prompt(user_prompt)
        print("\nAnalysis complete. Configuring adaptive crew...\n")
        
        # Parse the analysis and configure the crew
        agent_configs = self.parse_analysis(analysis)
        self.configure_from_analysis(agent_configs)
        
        # Create and run the crew
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew tasks
        result = crew.kickoff()
        return result

# Example usage
if __name__ == "__main__":
    adaptive_crew = AdaptiveCrew()
    
    # Get user input
    user_prompt = input("Enter your prompt for the AI team: ")
    
    # Process the prompt
    result = adaptive_crew.process_prompt(user_prompt)
    
    print("\n========== FINAL RESULT ==========\n")
    print(result)
