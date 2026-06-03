from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Debate2():
    """Debate2 crew"""

    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'

 
    @agent
    def debater(self) -> Agent:
        return Agent(
            config=self.agents_config['debater'],verbose=True)

    @agent
    def judge(self) -> Agent:
        return Agent(config=self.agents_config['judge'], verbose=True)


    @task
    def propose_task(self) -> Task:
        return Task(config=self.tasks_config['propose_task'])

    @task
    def oppose_task(self) -> Task:
        return Task(config=self.tasks_config['oppose_task'])

    @task
    def decide_task(self) -> Task:
        return Task(config=self.tasks_config['decide_task'])

    @crew
    def crew(self) -> Crew:
        """Creates the Debate2 crew"""
      

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
