cat > src/kite_historical_data/tool.py << 'EOF'
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import os
import requests
from datetime import datetime


class KiteHistoricalDataInput(BaseModel):
    instrument_token: int = Field(..., description="Instrument token for the stock")
    from_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    to_date: str = Field(..., description="End date in YYYY-MM-DD format")
    interval: str = Field(default="day", description="Candle interval: minute, 3minute, 5minute, 10minute, 15minute, 30minute, 60minute, day")


class KiteHistoricalData(BaseTool):
    name: str = "Kite Historical Data"
    description: str = "Fetches historical OHLCV candle data for a given instrument token and date range from Zerodha Kite Connect API."
    args_schema: type[BaseModel] = KiteHistoricalDataInput

    def _run(self, instrument_token: int, from_date: str, to_date: str, interval: str = "day") -> str:
        api_key = os.environ.get("KITE_API_KEY")
        access_token = os.environ.get("KITE_ACCESS_TOKEN")

        if not api_key or not access_token:
            return "Error: KITE_API_KEY and KITE_ACCESS_TOKEN environment variables are required."

        url = f"https://api.kite.trade/instruments/historical/{instrument_token}/{interval}"
        headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {api_key}:{access_token}"
        }
        params = {
            "from": from_date,
            "to": to_date
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            candles = data.get("data", {}).get("candles", [])
            if not candles:
                return "No data returned for the given parameters."
            result = f"Historical data for token {instrument_token} ({interval}):\n"
            result += "Date, Open, High, Low, Close, Volume\n"
            for c in candles[-20:]:  # Return last 20 candles
                result += f"{c[0]}, {c[1]}, {c[2]}, {c[3]}, {c[4]}, {c[5]}\n"
            return result
        except Exception as e:
            return f"Error fetching historical data: {str(e)}"
EOF
