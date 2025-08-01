from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup

@CrewBase
class WebscraperCrew:
    """web_scraper crew"""

    def simple_fetch(self, url: str) -> str:
        """
        基于 requests 的简单爬虫方法，返回页面 HTML
        """
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text

    def parse_text(self, html: str) -> str:
        """
        基于 BeautifulSoup 的文本提取方法，将 HTML 转为纯文本
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

    @agent
    def web_scraper(self) -> Agent:
        # 直接创建 BaseTool 实例
        fetch_tool = BaseTool(
            name="simple_fetch",
            func=self.simple_fetch,
            description="Fetch HTML content from a URL",
        )
        return Agent(
            config=self.agents_config["web_scraper"],
            tools=[fetch_tool],
            verbose=True,
        )

    @agent
    def data_extractor(self) -> Agent:
        # 直接创建 BaseTool 实例
        extractor_tool = BaseTool(
            name="parse_text",
            func=self.parse_text,
            description="Extract plain text from HTML",
        )
        return Agent(
            config=self.agents_config["data_extractor"],
            tools=[extractor_tool],
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
