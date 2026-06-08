
from typing import Dict, List
from datetime import datetime


def get_share_price(symbol: str) -> float:
    """
    Simulates retrieving the current market price for a given stock symbol.
    Uses fixed test prices for demonstration purposes.
    
    Args:
        symbol: Stock symbol to get the price for.
        
    Returns:
        float: Current price of the stock, or 0.0 if symbol not found.
    """
    prices = {'AAPL': 150.00, 'TSLA': 650.00, 'GOOGL': 2800.00}
    return prices.get(symbol, 0.0)


class Account:
    """
    A simple account management system for a trading simulation platform.
    
    Handles user account creation, fund management, and stock transaction logging.
    Provides methods to report on current holdings, transaction history, and profit/loss.
    """
    
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        """
        Initializes an account with a unique ID and an initial deposit amount.
        
        Args:
            account_id: Unique identifier for the account.
            initial_deposit: The initial amount of money deposited in the account.
        """
        self.account_id = account_id
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.portfolio: Dict[str, int] = {}
        self.transaction_history: List[Dict] = []
        
        # Record initial deposit as a transaction
        self.transaction_history.append({
            'type': 'deposit',
            'amount': initial_deposit,
            'timestamp': datetime.now().isoformat(),
            'balance_after': self.balance
        })
    
    def deposit(self, amount: float) -> None:
        """
        Adds the specified amount to the account balance.
        
        Args:
            amount: The amount of money to deposit.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        
        # Record the deposit transaction
        self.transaction_history.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'balance_after': self.balance
        })
    
    def withdraw(self, amount: float) -> bool:
        """
        Attempts to subtract the specified amount from the account balance.
        Checks if the balance is sufficient.
        
        Args:
            amount: The amount of money to withdraw.
            
        Returns:
            bool: True if the withdrawal is successful, False otherwise.
        """
        if amount <= 0:
            return False
        
        if self.balance >= amount:
            self.balance -= amount
            
            # Record the withdrawal transaction
            self.transaction_history.append({
                'type': 'withdrawal',
                'amount': amount,
                'timestamp': datetime.now().isoformat(),
                'balance_after': self.balance
            })
            return True
        
        return False
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """
        Attempts to buy a specified quantity of shares at the current market price.
        Updates balance and portfolio if successful.
        
        Args:
            symbol: Stock symbol to purchase.
            quantity: Number of shares to buy.
            
        Returns:
            bool: True if the purchase is successful, False otherwise based on available balance.
        """
        if quantity <= 0:
            return False
        
        price = get_share_price(symbol)
        
        if price == 0.0:
            return False
        
        total_cost = price * quantity
        
        if self.balance >= total_cost:
            self.balance -= total_cost
            
            # Update portfolio
            if symbol in self.portfolio:
                self.portfolio[symbol] += quantity
            else:
                self.portfolio[symbol] = quantity
            
            # Record the buy transaction
            self.transaction_history.append({
                'type': 'buy',
                'symbol': symbol,
                'quantity': quantity,
                'price_per_share': price,
                'total_cost': total_cost,
                'timestamp': datetime.now().isoformat(),
                'balance_after': self.balance
            })
            return True
        
        return False
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """
        Attempts to sell a specified quantity of shares at the current market price.
        Updates balance and portfolio if successful.
        
        Args:
            symbol: Stock symbol to sell.
            quantity: Number of shares to sell.
            
        Returns:
            bool: True if the sale is successful, False if there are insufficient shares.
        """
        if quantity <= 0:
            return False
        
        # Check if user has enough shares
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            return False
        
        price = get_share_price(symbol)
        
        if price == 0.0:
            return False
        
        total_proceeds = price * quantity
        
        self.balance += total_proceeds
        
        # Update portfolio
        self.portfolio[symbol] -= quantity
        
        # Remove symbol from portfolio if quantity reaches 0
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        # Record the sell transaction
        self.transaction_history.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_proceeds': total_proceeds,
            'timestamp': datetime.now().isoformat(),
            'balance_after': self.balance
        })
        return True
    
    def calculate_portfolio_value(self) -> float:
        """
        Calculates and returns the total value of the user's portfolio based on current market prices.
        
        Returns:
            float: Total value of the current holdings.
        """
        total_value = 0.0
        
        for symbol, quantity in self.portfolio.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        
        return total_value
    
    def calculate_profit_loss(self) -> float:
        """
        Calculates the profit or loss from the initial deposit to the current portfolio value.
        
        Returns:
            float: Net profit (+) or loss (-).
        """
        current_total_value = self.balance + self.calculate_portfolio_value()
        return current_total_value - self.initial_deposit
    
    def report_holdings(self) -> Dict[str, int]:
        """
        Provides a snapshot of the user's current holdings.
        
        Returns:
            Dict[str, int]: Dictionary with stock symbols as keys and quantities as values.
        """
        return self.portfolio.copy()
    
    def report_transactions(self) -> List[Dict]:
        """
        Returns the list of all transactions made by the user.
        
        Returns:
            List[Dict]: List of transaction records, each with details and timestamps.
        """
        return self.transaction_history.copy()
