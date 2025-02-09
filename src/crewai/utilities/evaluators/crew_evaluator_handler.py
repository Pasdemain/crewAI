import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

from langchain.base_language.base_language_model import BaseLanguageModel
from pydantic import BaseModel, Field, InstanceOf
from rich.box import HEAVY_EDGE
from rich.console import Console
from rich.table import Table

from crewai.agent import Agent
from crewai.llm import LLM
from crewai.task import Task
from crewai.tasks.task_output import TaskOutput
from crewai.telemetry import Telemetry
from crewai.utilities.logger import Logger


class TaskEvaluationPydanticOutput(BaseModel):
    quality: float = Field(
        description="A score from 1 to 10 evaluating on completion, quality, and overall performance from the task_description and task_expected_output to the actual Task Output."
    )


class CrewEvaluator:
    """
    A class to evaluate the performance of the agents in the crew based on the tasks they have performed.

    Attributes:
        crew (Crew): The crew of agents to evaluate
        llm (Union[str, LLM, BaseLanguageModel]): Language model to use for evaluation
        tasks_scores (defaultdict): Dictionary to store the scores of the agents for each task
        iteration (int): Current iteration of the evaluation
        run_execution_times (defaultdict): Dictionary to store execution times for each run
    """

    tasks_scores: defaultdict = defaultdict(list)
    run_execution_times: defaultdict = defaultdict(list)
    iteration: int = 0

    def __init__(self, crew, llm: Union[str, InstanceOf[LLM], BaseLanguageModel]):
        """Initialize the CrewEvaluator.
        
        Args:
            crew (Crew): The crew to evaluate
            llm (Union[str, LLM, BaseLanguageModel]): Language model to use for evaluation
        
        Raises:
            ValueError: If llm is of an unsupported type
        """
        if not isinstance(llm, (str, LLM, BaseLanguageModel, type(None))):
            raise ValueError(f"Unsupported LLM type: {type(llm)}")

        self.crew = crew
        self.llm = llm
        self._telemetry = Telemetry()
        self._logger = Logger()
        self._setup_llm()
        self._setup_for_evaluating()

    def _setup_llm(self):
        """Set up the LLM following the Agent class pattern.
        
        This method initializes the language model based on the provided llm parameter:
        - If string: creates new LLM instance with model name
        - If LLM instance: uses as-is
        - If None: uses default model from environment or "gpt-4"
        - Otherwise: attempts to extract model name from object attributes
        """
        if isinstance(self.llm, str):
            self.llm = LLM(model=self.llm)
        elif isinstance(self.llm, LLM):
            pass
        elif self.llm is None:
            model_name = os.environ.get("OPENAI_MODEL_NAME") or "gpt-4"
            self.llm = LLM(model=model_name)
        else:
            llm_params = {
                "model": getattr(self.llm, "model_name", None)
                or getattr(self.llm, "deployment_name", None)
                or str(self.llm),
            }
            self.llm = LLM(**llm_params)


    def _setup_for_evaluating(self) -> None:
        """Sets up the crew for evaluating."""
        for task in self.crew.tasks:
            task.callback = self.evaluate

    def _evaluator_agent(self):
        return Agent(
            role="Task Execution Evaluator",
            goal=(
                "Your goal is to evaluate the performance of the agents in the crew based on the tasks they have performed using score from 1 to 10 evaluating on completion, quality, and overall performance."
            ),
            backstory="Evaluator agent for crew evaluation with precise capabilities to evaluate the performance of the agents in the crew based on the tasks they have performed",
            verbose=False,
            llm=self.llm,
        )

    def _evaluation_task(
        self, evaluator_agent: Agent, task_to_evaluate: Task, task_output: str
    ) -> Task:
        return Task(
            description=(
                "Based on the task description and the expected output, compare and evaluate the performance of the agents in the crew based on the Task Output they have performed using score from 1 to 10 evaluating on completion, quality, and overall performance."
                f"task_description: {task_to_evaluate.description} "
                f"task_expected_output: {task_to_evaluate.expected_output} "
                f"agent: {task_to_evaluate.agent.role if task_to_evaluate.agent else None} "
                f"agent_goal: {task_to_evaluate.agent.goal if task_to_evaluate.agent else None} "
                f"Task Output: {task_output}"
            ),
            expected_output="Evaluation Score from 1 to 10 based on the performance of the agents on the tasks",
            agent=evaluator_agent,
            output_pydantic=TaskEvaluationPydanticOutput,
        )

    def set_iteration(self, iteration: int) -> None:
        self.iteration = iteration

    def print_crew_evaluation_result(self) -> None:
        """
        Prints the evaluation result of the crew in a table.
        A Crew with 2 tasks using the command crewai test -n 3
        will output the following table:

                        Tasks Scores
                    (1-10 Higher is better)
        ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Tasks/Crew/Agents  ┃ Run 1 ┃ Run 2 ┃ Run 3 ┃ Avg. Total ┃ Agents                       ┃
        ┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
        │ Task 1             │ 9.0   │ 10.0  │ 9.0   │ 9.3        │ - AI LLMs Senior Researcher  │
        │                    │       │       │       │            │ - AI LLMs Reporting Analyst  │
        │                    │       │       │       │            │                              │
        │ Task 2             │ 9.0   │ 9.0   │ 9.0   │ 9.0        │ - AI LLMs Senior Researcher  │
        │                    │       │       │       │            │ - AI LLMs Reporting Analyst  │
        │                    │       │       │       │            │                              │
        │ Crew               │ 9.0   │ 9.5   │ 9.0   │ 9.2        │                              │
        │ Execution Time (s) │ 42    │ 79    │ 52    │ 57         │                              │
        └────────────────────┴───────┴───────┴───────┴────────────┴──────────────────────────────┘
        """
        task_averages = [
            sum(scores) / len(scores) for scores in zip(*self.tasks_scores.values())
        ]
        crew_average = sum(task_averages) / len(task_averages)

        table = Table(title="Tasks Scores \n (1-10 Higher is better)", box=HEAVY_EDGE)

        table.add_column("Tasks/Crew/Agents", style="cyan")
        for run in range(1, len(self.tasks_scores) + 1):
            table.add_column(f"Run {run}", justify="center")
        table.add_column("Avg. Total", justify="center")
        table.add_column("Agents", style="green")

        for task_index, task in enumerate(self.crew.tasks):
            task_scores = [
                self.tasks_scores[run][task_index]
                for run in range(1, len(self.tasks_scores) + 1)
            ]
            avg_score = task_averages[task_index]
            agents = list(task.processed_by_agents)

            # Add the task row with the first agent
            table.add_row(
                f"Task {task_index + 1}",
                *[f"{score:.1f}" for score in task_scores],
                f"{avg_score:.1f}",
                f"- {agents[0]}" if agents else "",
            )

            # Add rows for additional agents
            for agent in agents[1:]:
                table.add_row("", "", "", "", "", f"- {agent}")

            # Add a blank separator row if it's not the last task
            if task_index < len(self.crew.tasks) - 1:
                table.add_row("", "", "", "", "", "")

        # Add Crew and Execution Time rows
        crew_scores = [
            sum(self.tasks_scores[run]) / len(self.tasks_scores[run])
            for run in range(1, len(self.tasks_scores) + 1)
        ]
        table.add_row(
            "Crew",
            *[f"{score:.2f}" for score in crew_scores],
            f"{crew_average:.1f}",
            "",
        )

        run_exec_times = [
            int(sum(tasks_exec_times))
            for _, tasks_exec_times in self.run_execution_times.items()
        ]
        execution_time_avg = int(sum(run_exec_times) / len(run_exec_times))
        table.add_row(
            "Execution Time (s)", *map(str, run_exec_times), f"{execution_time_avg}", ""
        )

        console = Console()
        console.print(table)

    def evaluate(self, task_output: TaskOutput):
        """Evaluates the performance of the agents in the crew based on the tasks they have performed.
        
        Args:
            task_output (TaskOutput): The output from the task to evaluate

        Raises:
            ValueError: If task to evaluate or task output is missing, or if evaluation result is invalid
        """
        current_task = None
        for task in self.crew.tasks:
            if task.description == task_output.description:
                current_task = task
                break

        if not current_task or not task_output:
            raise ValueError(
                "Task to evaluate and task output are required for evaluation"
            )

        evaluator_agent = self._evaluator_agent()
        evaluation_task = self._evaluation_task(
            evaluator_agent, current_task, task_output.raw
        )

        evaluation_result = evaluation_task.execute_sync()

        if isinstance(evaluation_result.pydantic, TaskEvaluationPydanticOutput):
            self._test_result_span = self._telemetry.individual_test_result_span(
                self.crew,
                evaluation_result.pydantic.quality,
                current_task._execution_time,
                self.llm,
            )
            self.tasks_scores[self.iteration].append(evaluation_result.pydantic.quality)
            self.run_execution_times[self.iteration].append(
                current_task._execution_time
            )
        else:
            raise ValueError("Evaluation result is not in the expected format")
