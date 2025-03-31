from typing import Optional, List, Dict, Any
import pandas as pd
from agno.tools import Toolkit
from agno.utils.log import logger


class StockTools(Toolkit):
    def __init__(self):
        """Initialize the StockTools toolkit for fetching financial data using akshare."""
        super().__init__(name="stock_tools")
        
        # Register all methods
        self.register(self.get_stock_info)
        self.register(self.get_stock_history)
        self.register(self.get_index_data)
        self.register(self.get_fund_data)
        self.register(self.get_forex_data)
        self.register(self.get_futures_data)
        self.register(self.get_bond_data)
        
    def get_stock_info(self, symbol: str) -> str:
        """
        Get basic information about a stock.
        
        For A-shares, use codes like "600519" (Maotai). For US stocks, use symbols like "AAPL" (Apple).
        
        Args:
            symbol (str): Stock symbol, e.g., "600519" for Maotai, "AAPL" for Apple
            
        Returns:
            str: Basic stock information including name, industry, market value, etc. as a formatted string
            
        Examples:
            > get_stock_info("600519")  # Get info for Maotai
            > get_stock_info("AAPL")    # Get info for Apple
        """
        try:
            import akshare as ak
            logger.info(f"Fetching stock info for symbol: {symbol}")
            
            # Determine if it's A-share or US stock
            if symbol.isdigit() or (len(symbol) == 6 and symbol[0] in ['0', '3', '6']):
                # A-share stocks
                stock_info = ak.stock_individual_info_em(symbol=symbol)
                if not stock_info.empty:
                    # Format the dataframe as a string
                    result = "股票基本信息：\n"
                    for _, row in stock_info.iterrows():
                        result += f"{row['item']}: {row['value']}\n"
                    return result
                return "错误：未找到股票信息"
            else:
                # US stocks
                stock_info = ak.stock_us_fundamental(symbol=symbol)
                if not stock_info.empty:
                    # Format as string
                    result = "Stock Information:\n"
                    for key, value in stock_info.iloc[0].items():
                        result += f"{key}: {value}\n"
                    return result
                return "Error: Stock information not found"
                
        except Exception as e:
            logger.warning(f"Failed to get stock info: {e}")
            return f"Error: {str(e)}"
    
    def get_stock_history(self, symbol: str, period: str = "daily", 
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None, 
                         adjust: str = "qfq") -> str:
        """
        Get historical stock price data for a given symbol.
        
        Retrieves OHLCV (Open, High, Low, Close, Volume) data for stocks. For A-shares, 
        different adjustment methods are available. Data can be filtered by date range.
        
        Args:
            symbol (str): Stock symbol (e.g., "600519" for Maotai, "AAPL" for Apple)
            period (str): Data frequency - "daily", "weekly", or "monthly"
            start_date (str, optional): Start date in format YYYYMMDD (e.g., "20230101")
            end_date (str, optional): End date in format YYYYMMDD (e.g., "20230131")
            adjust (str): Price adjustment method - "qfq" (forward), "hfq" (backward), or "" (none)
            
        Returns:
            Dict[str, Any]: Historical stock data with preview, shape, columns and statistics
            
        Examples:
            > get_stock_history("600519")  # Default daily data with qfq adjustment
            > get_stock_history("AAPL", period="weekly", start_date="20230101", end_date="20230630")
            > get_stock_history("000001", adjust="hfq")  # Backward adjusted prices
        """
        try:
            import akshare as ak
            logger.info(f"Fetching stock history for {symbol}, period={period}, adjust={adjust}")
            
            # For A-share stocks
            if symbol.isdigit() or (len(symbol) == 6 and symbol[0] in ['0', '3', '6']):
                if period == "daily":
                    df = ak.stock_zh_a_hist(symbol=symbol, period=period, 
                                          start_date=start_date, end_date=end_date, 
                                          adjust=adjust)
                elif period == "weekly":
                    df = ak.stock_zh_a_hist(symbol=symbol, period="weekly", 
                                          adjust=adjust)
                elif period == "monthly":
                    df = ak.stock_zh_a_hist(symbol=symbol, period="monthly", 
                                          adjust=adjust)
                else:
                    return {"error": "Invalid period. Choose from 'daily', 'weekly', 'monthly'"}
            # For US stocks
            else:
                df = ak.stock_us_daily(symbol=symbol)
                
            if df.empty:
                return {"error": "No historical data found"}
                
            # Format as string
            result = f"股票历史数据 ({symbol}):\n"
            result += f"数据周期: {period}\n"
            result += f"数据行数: {df.shape[0]}, 列数: {df.shape[1]}\n"
            result += f"列名: {', '.join(df.columns.tolist())}\n\n"
            result += "最近数据预览:\n"
            result += df.head(10).to_string()
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get stock history: {e}")
            return f"错误: {str(e)}"
    
    def get_index_data(self, index_code: str, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> str:
        """
        Get market index historical data.
        
        Retrieves historical data for major market indices from China and US markets.
        
        Args:
            index_code (str): Index code
                - Chinese indices: "000001" (SSE Composite), "399001" (SZSE Component)
                - US indices: "SPX" (S&P 500), "DJI" (Dow Jones), "IXIC" (NASDAQ)
            start_date (str, optional): Start date in format YYYYMMDD (e.g., "20230101")
            end_date (str, optional): End date in format YYYYMMDD (e.g., "20230131")
            
        Returns:
            Dict[str, Any]: Index data with preview, shape and columns information
            
        Examples:
            > get_index_data("000001")  # Shanghai Composite Index
            > get_index_data("SPX", start_date="20230101", end_date="20230630")  # S&P 500
        """
        try:
            import akshare as ak
            logger.info(f"Fetching index data for {index_code}")
            
            # For Chinese indices
            if index_code.startswith("0") or index_code.startswith("3"):
                df = ak.index_zh_a_hist(symbol=index_code, start_date=start_date, end_date=end_date)
            # For US indices
            elif index_code in ["SPX", "DJI", "IXIC"]:
                mapping = {"SPX": "^GSPC", "DJI": "^DJI", "IXIC": "^IXIC"}
                df = ak.index_us_stock_hist(symbol=mapping.get(index_code, index_code))
            else:
                return {"error": "Unsupported index code"}
                
            if df.empty:
                return {"error": "No index data found"}
                
            # Format as string
            result = f"指数数据 ({index_code}):\n"
            result += f"数据行数: {df.shape[0]}, 列数: {df.shape[1]}\n"
            result += f"列名: {', '.join(df.columns.tolist())}\n\n"
            result += "最近数据预览:\n"
            result += df.head(10).to_string()
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get index data: {e}")
            return f"错误: {str(e)}"
    
    def get_fund_data(self, fund_code: str, fund_type: str = "fund_open") -> str:
        """
        Get mutual fund or ETF data.
        
        Retrieves information and NAV history for mutual funds and ETFs in China.
        
        Args:
            fund_code (str): Fund code, e.g., "000001" for a specific fund
            fund_type (str): Fund type - "fund_open" for open-ended funds, "fund_etf" for ETFs
            
        Returns:
            Dict[str, Any]: Fund information and NAV history data
            
        Examples:
            > get_fund_data("000001")  # Default open-ended fund
            > get_fund_data("510050", fund_type="fund_etf")  # ETF fund
        """
        try:
            import akshare as ak
            logger.info(f"Fetching fund data for {fund_code}, type={fund_type}")
            
            if fund_type == "fund_open":
                df = ak.fund_open_fund_info_em(fund=fund_code)
                nav_df = ak.fund_open_fund_info_em(fund=fund_code, indicator="单位净值走势")
                
                # Format as string
                result = f"基金数据 ({fund_code}):\n"
                if not df.empty:
                    result += "基金基本信息:\n"
                    result += df.to_string() + "\n\n"
                
                if not nav_df.empty:
                    result += "净值走势（最近10条）:\n"
                    result += nav_df.head(10).to_string()
                
            elif fund_type == "fund_etf":
                df = ak.fund_etf_fund_info_em(fund=fund_code)
                
                # Format as string
                result = f"ETF基金数据 ({fund_code}):\n"
                if not df.empty:
                    result += df.head(10).to_string()
                else:
                    result += "无数据"
                
            else:
                return "错误: 不支持的基金类型。请选择 'fund_open' 或 'fund_etf'"
                
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get fund data: {e}")
            return f"错误: {str(e)}"
    
    def get_forex_data(self, symbol: str = "USD/CNY", start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> str:
        """
        Get foreign exchange (forex) rate historical data.
        
        Retrieves exchange rate data between currency pairs.
        
        Args:
            symbol (str): Currency pair in format "XXX/YYY", e.g., "USD/CNY" for US Dollar to Chinese Yuan
            start_date (str, optional): Start date in format YYYYMMDD (e.g., "20230101")
            end_date (str, optional): End date in format YYYYMMDD (e.g., "20230131")
            
        Returns:
            Dict[str, Any]: Forex historical data with preview, shape and columns information
            
        Examples:
            > get_forex_data()  # Default USD/CNY
            > get_forex_data("EUR/USD")  # Euro to US Dollar
            > get_forex_data("GBP/JPY", start_date="20230101", end_date="20230630")
        """
        try:
            import akshare as ak
            logger.info(f"Fetching forex data for {symbol}")
            
            if symbol == "USD/CNY":
                # For USD/CNY exchange rate
                df = ak.currency_history_fx_spot(symbol="USDCNY")
            else:
                # For other currency pairs
                currency_from, currency_to = symbol.split('/')
                df = ak.currency_history_fx_spot(symbol=f"{currency_from}{currency_to}")
                
            if df.empty:
                return {"error": "No forex data found"}
                
            # Format as string
            result = f"外汇数据 ({symbol}):\n"
            result += f"数据行数: {df.shape[0]}, 列数: {df.shape[1]}\n"
            result += f"列名: {', '.join(df.columns.tolist())}\n\n"
            result += "最近数据预览:\n"
            result += df.head(10).to_string()
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get forex data: {e}")
            return f"错误: {str(e)}"
    
    def get_futures_data(self, symbol: str, period: str = "daily") -> str:
        """
        Get futures contract market data.
        
        Retrieves historical price data for futures contracts in Chinese markets.
        
        Args:
            symbol (str): Futures contract symbol
                - Common contracts: "AU" (Gold), "CU" (Copper), "AL" (Aluminum)
                - Agricultural: "A" (Soybean), "C" (Corn), "M" (Meal)
                - Energy: "SC" (Crude Oil), "FU" (Fuel Oil)
            period (str): Data frequency - "daily", "weekly", "monthly"
            
        Returns:
            Dict[str, Any]: Futures data with preview, shape and columns information
            
        Examples:
            > get_futures_data("AU")  # Gold futures, daily data
            > get_futures_data("CU", period="weekly")  # Copper futures, weekly data
        """
        try:
            import akshare as ak
            logger.info(f"Fetching futures data for {symbol}, period={period}")
            
            if period == "daily":
                df = ak.futures_main_sina(symbol=symbol)
            elif period == "weekly":
                df = ak.futures_main_sina(symbol=symbol, period="weekly")
            elif period == "monthly":
                df = ak.futures_main_sina(symbol=symbol, period="monthly")
            else:
                return {"error": "Invalid period. Choose from 'daily', 'weekly', 'monthly'"}
                
            if df.empty:
                return {"error": "No futures data found"}
                
            # Format as string
            result = f"期货数据 ({symbol}, {period}):\n"
            result += f"数据行数: {df.shape[0]}, 列数: {df.shape[1]}\n"
            result += f"列名: {', '.join(df.columns.tolist())}\n\n"
            result += "最近数据预览:\n"
            result += df.head(10).to_string()
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get futures data: {e}")
            return f"错误: {str(e)}"
    
    def get_bond_data(self, symbol: str) -> str:
        """
        Get bond market data.
        
        Retrieves information for bonds in Chinese markets.
        
        Args:
            symbol (str): Bond code or type identifier
                - Convertible bonds: 6-digit codes starting with "1" or "2", e.g., "110059"
                - Treasury bonds: Use prefix "treasury_" + curve name
            
        Returns:
            Dict[str, Any]: Bond data or yield curve information
            
        Examples:
            > get_bond_data("110059")  # Specific convertible bond
            > get_bond_data("treasury_china")  # Chinese treasury yield curve
        """
        try:
            import akshare as ak
            logger.info(f"Fetching bond data for {symbol}")
            
            # For convertible bonds
            if len(symbol) == 6 and symbol.startswith(("1", "2")):
                df = ak.bond_cb_jsl()
                if not df.empty:
                    filtered_df = df[df["bond_id"] == symbol]
                    if not filtered_df.empty:
                        # Format as string
                        bond_data = filtered_df.iloc[0]
                        result = f"可转债数据 ({symbol}):\n"
                        for key, value in bond_data.items():
                            result += f"{key}: {value}\n"
                        return result
                return "错误: 未找到债券"
                
            # For treasury bonds
            elif symbol.startswith("treasury_"):
                curve_name = symbol.replace("treasury_", "")
                df = ak.bond_china_yield(start_date="20200101")
                if not df.empty:
                    # Format as string
                    result = f"国债收益率曲线数据:\n"
                    result += f"数据行数: {df.shape[0]}, 列数: {df.shape[1]}\n"
                    result += f"列名: {', '.join(df.columns.tolist())}\n\n"
                    result += "最近数据预览:\n"
                    result += df.head(10).to_string()
                    return result
                return "错误: 未找到债券数据"
            
            else:
                return "错误: 不支持的债券符号格式"
                
        except Exception as e:
            logger.warning(f"Failed to get bond data: {e}")
            return f"错误: {str(e)}"