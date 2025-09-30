from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import JSONSearchTool, TavilySearchTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from typing import List, Optional
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


class SubTopic(BaseModel):
    name: str
    description: str

class Topics(BaseModel):
    main_topic: str
    sub_topics: List[SubTopic]

class NewsItem(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    summary: Optional[str] = None
    relevance_score: Optional[float] = None  # model- or rule-derived

class SubtopicNews(BaseModel):
    sub_topic: SubTopic
    articles: List[NewsItem]

class CombinedNews(BaseModel):
    main_topic: str
    sub_topics: List[SubtopicNews]
    
    
tavily_tool = TavilySearchTool()
json_search_tool = JSONSearchTool(json_path='./config/topics.json')

@CrewBase
class AiNews():
    """AiNews crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def news_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['news_researcher'], # type: ignore[index],
            tools=[json_search_tool, tavily_tool],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['news_research_task'], # type: ignore[index]
            output_pydantic=CombinedNews
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AiNews crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
