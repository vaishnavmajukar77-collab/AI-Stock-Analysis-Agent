from google.adk.agents.llm_agent import Agent
from .prompt import ROOT_AGENT_INSTRUCTIONS
from google.adk.tools import AgentTool
from .company_info_agent import company_info
from .news_agent import news_agent
from .technical_indicator_agent import technical_indicator_agent

# pyrefly: ignore [missing-import]
from google.adk.agents import SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os

load_dotenv()
from .company_info_agent import get_company_profile
from .news_agent import get_company_news
from .technical_indicator_agent import get_technical_indicators

# information_agent=SequentialAgent(
#     name="AllInformationAgent",
#      sub_agents=[
#         company_info,
#         news_agent,
#         technical_indicator_agent
#     ]
# )

root_agent = Agent(
    model="gemini-2.5-flash",
    name='stock_analysis_root_agent',
    description="Coordinates multiple specialized agents to perform comprehensive stock analysis "
        "by combining company fundamentals, recent news, and technical indicators into "
        "a structured investment recommendation."
,  
    instruction=ROOT_AGENT_INSTRUCTIONS,
    # tools=[AgentTool(agent=information_agent)]
      tools=[
        get_company_profile,
        get_company_news,
        get_technical_indicators
    ]
)
