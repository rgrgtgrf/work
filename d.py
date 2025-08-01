from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import requests
from bs4 import BeautifulSoup

@CrewBase
class WebscraperCrew:
    """web_scraper crew"""

    def simple_fetch(self, url: str) -> str:
        """
        基于 requests + BeautifulSoup 的简单爬虫工具
        返回原始 HTML 文本
        """
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text

    def parse_text(self, html: str) -> str:
        """
        将 HTML 转为纯文本
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

    @agent
    def web_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config["web_scraper"],
            tools=[self.simple_fetch],  # 只需传入 URL，返回 HTML
            verbose=True,
        )

    @agent
    def data_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["data_extractor"],
            tools=[self.parse_text],  # 将 HTML 转为纯文本
            verbose=True,
        )

    @agent
    def content_storer(self) -> Agent:
        # 假设 neon 工具配置不变
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
