import json
import os
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
from google.adk.agents.llm_agent import Agent

load_dotenv()


def get_order_book_data(company_name: str) -> dict:
    """
    Retrieves order book top-of-book quotes, bid/ask spread, volume liquidity ratios,
    and order imbalance metrics for a given company.
    """
    try:
        # 1. Search ticker
        search_results = yf.Search(company_name, max_results=1).quotes
        if not search_results:
            return {
                "agent": "OrderBookAgent",
                "status": "failed",
                "error": f"Could not resolve ticker for '{company_name}'"
            }

        ticker_symbol = search_results[0]['symbol']
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # 2. Extract market quotes & depth info
        regular_price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose") or 0.0
        bid = info.get("bid") or regular_price
        ask = info.get("ask") or regular_price
        bid_size = info.get("bidSize") or 0
        ask_size = info.get("askSize") or 0
        volume = info.get("volume") or info.get("regularMarketVolume") or 0
        avg_volume = info.get("averageVolume") or info.get("averageVolume10days") or 1

        # 3. Calculate Spread metrics
        spread = round(ask - bid, 4) if ask and bid else 0.0
        spread_pct = round((spread / ask * 100), 4) if ask and ask > 0 else 0.0

        # 4. Calculate Order Imbalance Ratio (Demand vs Supply pressure)
        total_depth_size = bid_size + ask_size
        if total_depth_size > 0:
            bid_ratio = round((bid_size / total_depth_size) * 100, 2)
            ask_ratio = round((ask_size / total_depth_size) * 100, 2)
        else:
            bid_ratio = 50.0
            ask_ratio = 50.0

        if bid_ratio > 55:
            order_pressure = "Net Buying Pressure (Demand Heavy)"
        elif ask_ratio > 55:
            order_pressure = "Net Selling Pressure (Supply Heavy)"
        else:
            order_pressure = "Balanced Order Flow"

        # 5. Volume Liquidity Assessment
        vol_ratio = round(volume / avg_volume, 2) if avg_volume > 0 else 1.0
        if vol_ratio >= 1.5:
            liquidity_status = "High Volume / Above Average Liquidity"
        elif vol_ratio <= 0.5:
            liquidity_status = "Low Volume / Below Average Liquidity"
        else:
            liquidity_status = "Normal Trading Liquidity"

        spread_assessment = "Tight Spread (High Efficiency)" if spread_pct <= 0.15 else "Wide Spread (Potential Slippage)"

        return {
            "agent": "OrderBookAgent",
            "status": "success",
            "company_name": info.get("longName") or info.get("shortName") or company_name,
            "ticker": ticker_symbol,
            "current_price": regular_price,
            "bid": bid,
            "ask": ask,
            "bid_size": bid_size,
            "ask_size": ask_size,
            "spread_dollars": spread,
            "spread_percentage": f"{spread_pct}%",
            "order_imbalance": {
                "bid_demand_share": f"{bid_ratio}%",
                "ask_supply_share": f"{ask_ratio}%",
                "pressure_sentiment": order_pressure
            },
            "liquidity": {
                "day_volume": volume,
                "average_volume": avg_volume,
                "relative_volume_ratio": vol_ratio,
                "liquidity_status": liquidity_status,
                "spread_assessment": spread_assessment
            },
            "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "source": "Yahoo Finance Realtime Depth API"
        }

    except Exception as e:
        return {
            "agent": "OrderBookAgent",
            "status": "failed",
            "error": str(e)
        }


order_book_agent = Agent(
    name="OrderBookAgent",
    model="gemini-2.5-flash",
    description="Retrieves top-of-book bid/ask quotes, order imbalance, spread percentage, and liquidity metrics.",
    instruction="""
You are OrderBookAgent.
Your only job is to retrieve top-of-book market order book and liquidity metrics.
Always use the get_order_book_data tool.
Never answer from your own memory or guess order book values.
Return only the structured output provided by the tool.
""",
    tools=[get_order_book_data]
)