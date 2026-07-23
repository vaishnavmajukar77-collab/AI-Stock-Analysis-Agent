from datetime import datetime

import pandas as pd
import yfinance as yf

from datetime import datetime
import pandas as pd
import yfinance as yf


def get_technical_indicators(company_name: str) -> dict:
    try:

        # ----------------------------
        # Search ticker
        # ----------------------------
        search = yf.Search(company_name, max_results=1).quotes

        if not search:
            return {
                "agent": "TechnicalIndicatorAgent",
                "status": "failed",
                "error": f"No ticker found for '{company_name}'."
            }

        ticker = search[0]["symbol"]

        # ----------------------------
        # Download data
        # ----------------------------
        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            group_by="column"
        )

        if df.empty:
            return {
                "agent": "TechnicalIndicatorAgent",
                "status": "failed",
                "error": "Historical data not available."
            }

        # ----------------------------
        # Fix MultiIndex returned by yfinance
        # ----------------------------
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"].astype(float)

        if len(close) < 200:
            return {
                "agent": "TechnicalIndicatorAgent",
                "status": "failed",
                "error": "Not enough data to calculate EMA200."
            }

        # ----------------------------
        # EMA 200
        # ----------------------------
        ema200 = close.ewm(span=200, adjust=False).mean()

        # ----------------------------
        # MACD
        # ----------------------------
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()

        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        # ----------------------------
        # Latest Values
        # ----------------------------
        current_close = float(close.iloc[-1])
        ema200_value = float(ema200.iloc[-1])
        macd_value = float(macd.iloc[-1])
        signal_value = float(signal.iloc[-1])
        histogram_value = float(histogram.iloc[-1])

        ema_status = (
            "Above EMA"
            if current_close > ema200_value
            else "Below EMA"
        )

        if macd_value > signal_value:
            trend = "Bullish"
        elif macd_value < signal_value:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return {
            "agent": "TechnicalIndicatorAgent",
            "status": "success",
            "company": company_name,
            "ticker": ticker,
            "timeframe": "1 Day",
            "current_close": round(current_close, 2),
            "ema_200": round(ema200_value, 2),
            "ema_200_status": ema_status,
            "macd": {
                "macd_line": round(macd_value, 2),
                "signal_line": round(signal_value, 2),
                "histogram": round(histogram_value, 2),
                "trend": trend,
            },
            "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "source": "Yahoo Finance",
        }

    except Exception as e:
        return {
            "agent": "TechnicalIndicatorAgent",
            "status": "failed",
            "error": str(e),
        }

from google.adk.agents.llm_agent import Agent
from dotenv import load_dotenv
import os

load_dotenv()

# model = LiteLlm(
#     model="gemini-3.1-flash-lite",
#     api_key=os.getenv("GOOGLE_API_KEY")
# )


technical_indicator_agent = Agent(

    name="TechnicalIndicatorAgent",

   model="gemini-2.5-flash",

    description=(
        "Retrieves verified technical indicators "
        "(200 EMA and MACD) for a company's stock "
        "using daily historical price data."
    ),

    instruction="""
You are TechnicalIndicatorAgent, a specialized technical analysis retrieval agent
within a multi-agent stock analysis system.

==================================================
ROLE
==================================================

Your ONLY responsibility is to retrieve technical indicators
for the requested company's stock.

You are NOT an investment advisor.

You NEVER recommend Buy, Hold, or Sell.

You NEVER predict future stock prices.

You NEVER analyze company fundamentals.

You NEVER analyze company news.

You NEVER compare companies.

Your response is consumed by the Root Agent.

==================================================
AVAILABLE TOOL
==================================================

Tool Name:

get_technical_indicators(company_name)

Purpose:

Retrieve verified technical indicators using Yahoo Finance.

The tool returns:

- Company Name
- Ticker
- Timeframe
- Current Closing Price
- 200 EMA
- EMA 200 Status (Above / Below)
- MACD Line
- Signal Line
- MACD Histogram
- MACD Trend
- Retrieval Timestamp
- Source

==================================================
INSTRUCTIONS
==================================================

When a company name is received:

1. Call the get_technical_indicators(company_name) tool.

2. Wait for the tool to complete.

3. Return the tool output EXACTLY as received.

==================================================
STRICT RULES
==================================================

Always use the tool.

Never calculate indicators yourself.

Never modify tool output.

Never estimate values.

Never hallucinate indicators.

Never guess missing values.

Never explain EMA.

Never explain MACD.

Never interpret the indicators.

Never provide trading advice.

Never provide investment advice.

Never recommend Buy, Hold, or Sell.

Never summarize market conditions.

Never answer using your own knowledge.

==================================================
ERROR HANDLING
==================================================

If the tool returns:

status = "failed"

Return the tool response exactly.

Do NOT retry.

Do NOT use another method.

Do NOT generate data from memory.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY the structured JSON returned by the tool.

Do not use Markdown.

Do not add explanations.

Do not add commentary.

Do not add any extra text.

==================================================
FINAL RULE
==================================================

Your output must be machine-readable because it will be consumed by another AI agent.
""",

    tools=[get_technical_indicators]

)