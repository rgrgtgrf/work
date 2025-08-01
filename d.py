import agentstack
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup

# 定义自定义工具，继承 BaseTool 并实现 _run 方法
class SimpleFetchTool(BaseTool):
    name: str = "simple_fetch"
    description: str = "Fetch HTML content from a URL using requests (limited)"
    max_chars: int = 1000  # 限制返回内容长度，默认 1000 字符

    def _run(self, url: str) -> str:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        text = resp.text
        # 截断过长内容，避免超出上下文长度
        return text[: self.max_chars]

class ParseTextTool(BaseTool):
    name: str = "parse_text"
    description: str = "Extract plain text from HTML using BeautifulSoup"
    max_chars: int = 1000  # 限制返回文本长度，默认 1000 字符

    def _run(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        # 同样截断文本
        return text[: self.max_chars]

@CrewBase
class WebscraperCrew:
    """web_scraper crew"""

    @agent
    def web_scraper(self) -> Agent:
        # 从 agents_config 中读取最大字符数配置
        max_chars = self.agents_config["web_scraper"].get("max_chars", SimpleFetchTool.max_chars)
        fetch_tool = SimpleFetchTool(max_chars=max_chars)
        return Agent(
            config=self.agents_config["web_scraper"],
            tools=[fetch_tool],
            verbose=True,
        )

    @agent
    def data_extractor(self) -> Agent:
        # 从 agents_config 中读取最大字符数配置
        max_chars = self.agents_config["data_extractor"].get("max_chars", ParseTextTool.max_chars)
        extractor_tool = ParseTextTool(max_chars=max_chars)
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
