from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional
from pydantic import BaseModel, Field
from crewai_tools import TavilySearchTool, ScrapeWebsiteTool


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


# --- Tools Definition ---
# Tavily Search Tool for the News Picker Agent
search_tool = TavilySearchTool()
# Scrape Website Tool for the Editor Agent to read article content
scrape_tool = ScrapeWebsiteTool()

class Article(BaseModel):
    headline: str = Field(description="News article headline")
    url: str = Field(description="URL of the news article")
    source: Optional[str] = Field(description="Source of the article (e.g., publisher name)")
    summary: Optional[str] = Field(description="A concise summary of the news article")
    relevance_score: float = Field(description="A score from 0.0 to 1.0 indicating relevance to the sub-topic")

class SubTopicSection(BaseModel):
    title: str = Field(description="The name of the sub-topic")
    editorial: str = Field(description="The editorial written for this sub-topic")

class SubTopic(BaseModel):
    sub_topic: SubTopicSection
    articles: List[Article] = Field(description="A list of 5 articles related to the sub-topic")

class MainTopic(BaseModel):
    title: str = Field(description="The main topic title, which is 'Cancer Health Care'")
    editorial: str = Field(description="The main editorial synthesizing all sub-topic editorials")
    articles: List[Article] = Field(description="The single best article chosen to be displayed on the home page")

class FinalReport(BaseModel):
    """The final, validated JSON report containing all generated content."""
    main_topic: MainTopic
    sub_topics: List[SubTopic]
    
# High-capability reasoning model for strategic planning
manager_llm = LLM(
    model="ollama/qwen3",  # Or the model you pulled
    base_url="http://localhost:11434"
)

@CrewBase
class HealthNewsPortal():
    """HealthNewsPortal crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # --- Agent Definitions ---
    @agent
    def project_manager_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['project_manager_agent'],
            verbose=True
        )
    
    @agent
    def news_picker_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['news_picker_agent'],
            tools=[search_tool],
            verbose=True,
        )

    @agent
    def editor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['editor_agent'],
            tools=[scrape_tool],
            verbose=True,
        )

    @agent
    def chief_editorial_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['chief_editorial_agent'],
            verbose=True,
        )

    @agent
    def qa_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_agent'],
            verbose=True,
        ) 
    
    
    # --- Task Definitions ---
    @task
    def manage_content_workflow_task(self) -> Task:
        return Task(
            config=self.tasks_config['manage_content_workflow_task'],
            agent=self.project_manager_agent()
        )
    
    @task
    def chief_editorial_task(self) -> Task:
        return Task(
            config=self.tasks_config['chief_editorial_task'],
            agent=self.chief_editorial_agent(),
            context=[self.manage_content_workflow_task()] # Depends on the manager's final compilation
        )
    
    @task
    def qa_task(self) -> Task:
        return Task(
            config=self.tasks_config['qa_task'],
            agent=self.qa_agent(),
            context=[self.chief_editorial_task()],
            output_json=FinalReport
        )
        
    
    # --- Crew Definition ---    
    @crew
    def crew(self) -> Crew:
        """Creates the HealthNewsPortal crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            manager_llm=manager_llm,
            verbose=True,
        )
