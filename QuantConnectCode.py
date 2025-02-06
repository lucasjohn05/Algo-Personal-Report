BASE COMPARISON TO S&P Program:
New Equity is $391,103.06->
To beat by >10%=> 430,213.37


---------------------------------------------------------------------------------------------Mean -Reversion-> Very Inefficent

from AlgorithmImports import *
from statsmodels.tsa.stattools import adfuller
import numpy as np

class MeanReversionStrategy(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Start Date
        self.SetEndDate(2024, 1, 1)    # End Date
        self.SetCash(100000)          # Starting Cash
        
        # Add multiple assets
        self.assets = ["SPY", "QQQ", "AAPL", "EURUSD", "GLD"]  # Equity, Forex, Gold
        self.symbols = [self.AddEquity(asset, Resolution.Daily).Symbol if asset != "EURUSD" 
                        else self.AddForex(asset, Resolution.Daily).Symbol for asset in self.assets]
        
        # Rolling windows for Z-score calculation
        self.lookback = 20
        self.data = {symbol: RollingWindow[float](self.lookback) for symbol in self.symbols}
        
        self.entry_zscore = 2.0
        self.exit_zscore = 0.5
        
        self.transaction_costs = 0.001  # Assumed cost per trade
        
    def OnData(self, data):
        for symbol in self.symbols:
            if symbol not in data or data[symbol] is None:
                continue
            
            price = data[symbol].Close
            self.data[symbol].Add(price)
            
            # Check if rolling window is ready
            if not self.data[symbol].IsReady:
                continue
            
            # Calculate rolling mean and std deviation
            prices = list(self.data[symbol])
            mean = np.mean(prices)
            std_dev = np.std(prices)
            z_score = (price - mean) / std_dev
            
            # Check stationarity using ADF test
            if self.IsMeanReverting(prices):
                if not self.Portfolio[symbol].Invested:
                    if z_score > self.entry_zscore:
                        self.SetHoldings(symbol, -0.1)  # Short position
                        self.Debug(f"SHORT {symbol} @ {price} | Z-Score: {z_score}")
                    elif z_score < -self.entry_zscore:
                        self.SetHoldings(symbol, 0.1)   # Long position
                        self.Debug(f"LONG {symbol} @ {price} | Z-Score: {z_score}")
                elif abs(z_score) < self.exit_zscore:
                    self.Liquidate(symbol)
                    self.Debug(f"EXIT {symbol} @ {price} | Z-Score: {z_score}")
    
    def IsMeanReverting(self, prices):
        # Perform ADF test and return True if p-value < 0.05
        result = adfuller(prices)
        p_value = result[1]
        return p_value < 0.05
    
    def OnEndOfDay(self):
        # Optional: Log daily portfolio stats
        self.Debug(f"Portfolio Value: {self.Portfolio.TotalPortfolioValue}")
---------------------------------------------------------------------------------------------

Momentum & Trade-Following

from AlgorithmImports import *
import numpy as np

class MomentumTrendFollowing(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)
        
        # Asset universe (can be expanded)
        self.assets = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
        self.symbols = [self.AddEquity(asset, Resolution.Daily).Symbol for asset in self.assets]
        
        # Momentum period and trend filter
        self.momentum_period = 126  # 6-month momentum
        self.trend_period = 200     # 200-day SMA
        
        # Rolling windows for momentum and trend
        self.momentum = {symbol: RollingWindow[float](self.momentum_period) for symbol in self.symbols}
        self.sma = {symbol: self.SMA(symbol, self.trend_period, Resolution.Daily) for symbol in self.symbols}
        
        # Rebalancing schedule
        self.rebalance_time = self.Time
        self.rebalance_period = timedelta(days=30)
    
    def OnData(self, data):
        if self.Time < self.rebalance_time:
            return
        
        # Update rebalance time
        self.rebalance_time = self.Time + self.rebalance_period
        
        # Calculate momentum and trend
        momentum_scores = {}
        for symbol in self.symbols:
            if symbol not in data or data[symbol] is None:
                continue
            
            price = data[symbol].Close
            self.momentum[symbol].Add(price)
            
            if not self.momentum[symbol].IsReady or not self.sma[symbol].IsReady:
                continue
            
            # Calculate 6-month momentum (percentage change)
            momentum_scores[symbol] = (price / self.momentum[symbol][0]) - 1
            
        # Filter by trend (price above 200-day SMA)
        ranked_assets = [symbol for symbol, score in sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True) if data[symbol].Close > self.sma[symbol].Current.Value]
        
        # Invest in top 3 assets
        if ranked_assets:
            weight = 1.0 / len(ranked_assets[:3])
            for symbol in self.Portfolio.Keys:
                if symbol not in ranked_assets[:3]:
                    self.Liquidate(symbol)
            for symbol in ranked_assets[:3]:
                self.SetHoldings(symbol, weight)

 





FINAL 

from AlgorithmImports import *

class AggressivePairsTrading(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2021, 12, 12)  # Start date
        self.SetEndDate(2024, 10, 1)    # End date
        self.SetCash(100000)  # Initial capital

        self.leverage = 3  # Use margin for aggressive trading
        self.pairs = [
    ("DPZ", "GOOG"), ("PEP", "XOM"), ("GME", "BABA"),
    ("KO", "SLV"), ("GME", "TLT"), ("TLT", "BABA"),
    ("BRK-B", "SLV"), ("DPZ", "BRK-B"),

    ("UNH", "LMT"), ("SLV", "MO"), ("UNH", "VTI"), 
    ("NFLX", "CAT"), ("UNH", "MO"), ("KO", "LMT")
    
]
        
        self.data = {}
        
        for stock1, stock2 in self.pairs:
            self.AddEquity(stock1, Resolution.Daily).SetLeverage(self.leverage)
            self.AddEquity(stock2, Resolution.Daily).SetLeverage(self.leverage)
            self.data[(stock1, stock2)] = []

        self.lookback = 30  # Lookback period for spread calculations

    def OnData(self, data):
     for stock1, stock2 in self.pairs:
        if stock1 in data and stock2 in data:
            price1 = data[stock1].Close
            price2 = data[stock2].Close

            self.data[(stock1, stock2)].append(price1 - price2)

            if len(self.data[(stock1, stock2)]) > self.lookback:
                self.data[(stock1, stock2)].pop(0)

            if len(self.data[(stock1, stock2)]) == self.lookback:
                spread = self.data[(stock1, stock2)]
                mean = sum(spread) / len(spread)
                std = np.std(spread)

                if std > 0:
                    z_score = (spread[-1] - mean) / std

                    # Define Position Sizing
                    position_size = min(self.Portfolio.Cash / 10_000, 0.3)  # Max 30% per pair

                    # Trading Logic
                    if z_score > 1.5 and not self.Portfolio[stock1].Invested:
                        self.SetHoldings(stock1, -position_size)  # Short stock1
                        self.SetHoldings(stock2, position_size)   # Long stock2

                    elif z_score < -1.5 and not self.Portfolio[stock1].Invested:
                        self.SetHoldings(stock1, position_size)  # Long stock1
                        self.SetHoldings(stock2, -position_size) # Short stock2

                    # Stop-loss and Exit
                    if self.Portfolio[stock1].UnrealizedProfitPercent < -0.03 or self.Portfolio[stock2].UnrealizedProfitPercent < -0.03:
                        self.Liquidate(stock1)
                        self.Liquidate(stock2)

                    elif -0.2 < z_score < 0.2:  # Exit if mean-reverted
                        self.Liquidate(stock1)
                        self.Liquidate(stock2)
