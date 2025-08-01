from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup

# 定义自定义工具，继承 BaseTool 并实现 _run 方法
class SimpleFetchTool(BaseTool):
    name: str = "simple_fetch"
    description: str = "Fetch HTML content from a URL using requests"

    def _run(self, url: str) -> str:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text

class ParseTextTool(BaseTool):
    name: str = "parse_text"
    description: str = "Extract plain text from HTML using BeautifulSoup"

    def _run(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

@CrewBase
class WebscraperCrew:
    """web_scraper crew"""

    @agent
    def web_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config["web_scraper"],
            tools=[SimpleFetchTool()],
            verbose=True,
        )

    @agent
    def data_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["data_extractor"],
            tools=[ParseTextTool()],
            verbose=True,
        )

    @agent
    def content_storer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_storer"],
            tools=[*agentstack.tools["neon"]],
            verbose=True,
        )

    @task
    def scrape_site(self) -> Task:
        return Task(
            config=self.tasks_config["scrape_site"],
        )

    @task
    def extract(self) -> Task:
        return Task(
            config=self.tasks_config["extract"],
        )

    @task
    def store(self) -> Task:
        return Task(
            config=self.tasks_config["store"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Test crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
