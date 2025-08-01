# src/crew.py

import os
import json
from dotenv import load_dotenv
import subprocess
import requests
import html2text
import neon_api
from bs4 import BeautifulSoup
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class WebscraperCrew:

    @agent
    def web_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config["web_scraper"],
            func=self.run_web_scraper,
            verbose=True,
        )

    async def run_web_scraper(self, task_input: dict) -> str:
        url = task_input.get("url")
        if not url:
            raise ValueError("web_scraper 需要参数 url")
        # 请求 HTML
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        html = resp.text
        # 转 Markdown
        conv = html2text.HTML2Text()
        conv.ignore_images = True
        conv.body_width = 0
        md = conv.handle(html)
        return md

    @agent
    def data_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["data_extractor"],
            func=self.run_data_extractor,
            verbose=True,
        )

    async def run_data_extractor(self, task_input: dict) -> str:
        md = task_input.get("markdown", "")
        lines = md.splitlines()
        posts = []
        for i, line in enumerate(lines):
            if line.startswith("## "):
                # 找到下一个列表项
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(("-", "*")):
                    j += 1
                while j < len(lines) and lines[j].strip().startswith(("-", "*")):
                    item = lines[j].lstrip("-* ").strip()
                    posts.append({"title": item, "author": "", "date": ""})
                    if len(posts) >= 20:
                        break
                    j += 1
            if len(posts) >= 20:
                break
        return json.dumps(posts, ensure_ascii=False)

    @agent
    def content_storer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_storer"],
            func=self.run_content_storer,
            verbose=True,
        )

    async def run_content_storer(self, task_input: dict) -> str:
        load_dotenv()
        conn_str = os.getenv("NEON_DATABASE_URL")
        if not conn_str:
            raise RuntimeError("请在 .env 文件中设置 NEON_DATABASE_URL")
        posts = json.loads(task_input.get("posts", "[]"))
        db = neon_api.connect(conn_str)
        with db.cursor() as cur:
            # 建表并清空
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                  id SERIAL PRIMARY KEY,
                  title TEXT NOT NULL,
                  author TEXT,
                  pub_date DATE
                );
                TRUNCATE posts;
            """)
            # 插入
            for p in posts:
                cur.execute(
                    "INSERT INTO posts (title, author, pub_date) VALUES (%s, %s, %s)",
                    (p["title"], p["author"], None)
                )
            db.commit()
            # 查询验证
            cur.execute("SELECT id, title, author, pub_date FROM posts ORDER BY id;")
            rows = cur.fetchall()
        db.close()
        return json.dumps(rows, ensure_ascii=False)

    @task
    def scrape_site(self) -> Task:
        return Task(config=self.tasks_config["scrape_site"])

    @task
    def extract(self) -> Task:
        return Task(config=self.tasks_config["extract"])

    @task
    def store(self) -> Task:
        return Task(config=self.tasks_config["store"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

