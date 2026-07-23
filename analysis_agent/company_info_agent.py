from google.adk.agents.llm_agent import Agent
import json
from datetime import datetime
import yfinance as yf


def get_company_profile(company_name: str) -> str:
    """
    Accepts a company name string, searches for it online,
    and returns a formatted JSON string containing full corporate/financial data.
    """
    try:
        # 1. Search for the ticker symbol based on the plain name
        search_results = yf.Search(company_name, max_results=1).quotes
        if not search_results:
            return json.dumps({
                "status": "failed",
                "error": f"Could not find any registered ticker for: '{company_name}'"
            }, indent=4)
            
        ticker_symbol = search_results[0]['symbol']
        
        # 2. Fetch the detailed data using the resolved ticker
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # 3. Format growth data accurately
        revenue_growth = info.get('revenueGrowth')
        revenue_growth_formatted = f"{round(revenue_growth * 100, 2)}%" if revenue_growth is not None else "N/A"
    
        # 4. Map values directly to your custom JSON schema
        schema = {
            "status": "success" if info.get('shortName') else "failed",
            "company_name": info.get('longName') or info.get('shortName') or company_name,
            "ticker": ticker_symbol,
            "sector": info.get('sector') or "N/A",
            "industry": info.get('industry') or "N/A",
            "market_cap": info.get('marketCap') or "N/A",
            "pe_ratio": info.get('trailingPE') or info.get('forwardPE') or "N/A",
            "annual_revenue": info.get('totalRevenue') or "N/A",
            "revenue_growth_yoy": revenue_growth_formatted,
            "total_debt": info.get('totalDebt') or "N/A",
            "exchange": info.get('exchange') or "N/A",
            "currency": info.get('currency') or "N/A",
            "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sources": ["Yahoo Finance Public Dataset Engine"]
        }
    
                
        return json.dumps(schema, indent=4)

    except Exception as e:
        return json.dumps({
            "status": "failed",
            "error": str(e)
        }, indent=4)

from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os

load_dotenv()



company_info = Agent(

    name="CompanyInfoAgent",

    model="gemini-2.5-flash",

    description="Retrieves verified company fundamental information.",

    instruction="""
You are CompanyInfoAgent.

Your only job is to retrieve company fundamental information.

Always use the get_company_profile tool.

Never answer from your own knowledge.

Never guess.

Never hallucinate.

Never calculate.

Never estimate.

Never search outside the tool.

If the tool succeeds,
return exactly the tool output.

If the tool fails,
return exactly the failure output.

Never provide investment advice.

Never provide Buy, Hold or Sell recommendations.

Never add explanations.

Return only the structured output from the tool.
""",

    tools=[get_company_profile]

)

