
import gradio as gr
from accounts import Account, get_share_price

# Global account instance - single user demo
account = None

def create_account(account_id: str, initial_deposit: float):
    """Create a new account with initial deposit."""
    global account
    try:
        if not account_id:
            return "Error: Account ID cannot be empty"
        if initial_deposit <= 0:
            return "Error: Initial deposit must be positive"
        account = Account(account_id, initial_deposit)
        return f"Account '{account_id}' created successfully with initial deposit: ${initial_deposit:.2f}"
    except Exception as e:
        return f"Error creating account: {str(e)}"

def deposit_funds(amount: float):
    """Deposit funds into the account."""
    global account
    if account is None:
        return "Error: No account exists. Please create an account first."
    try:
        account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}. New balance: ${account.balance:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def withdraw_funds(amount: float):
    """Withdraw funds from the account."""
    global account
    if account is None:
        return "Error: No account exists. Please create an account first."
    try:
        success = account.withdraw(amount)
        if success:
            return f"Successfully withdrew ${amount:.2f}. New balance: ${account.balance:.2f}"
        else:
            return f"Error: Insufficient funds. Current balance: ${account.balance:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def buy_shares_ui(symbol: str, quantity: int):
    """Buy shares."""
    global account
    if account is None:
        return "Error: No account exists. Please create an account first."
    try:
        price = get_share_price(symbol)
        if price == 0.0:
            return f"Error: Unknown symbol '{symbol}'. Available: AAPL, TSLA, GOOGL"
        
        total_cost = price * quantity
        success = account.buy_shares(symbol, quantity)
        if success:
            return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f}/share. Total cost: ${total_cost:.2f}. New balance: ${account.balance:.2f}"
        else:
            return f"Error: Insufficient funds. Need ${total_cost:.2f}, but balance is ${account.balance:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def sell_shares_ui(symbol: str, quantity: int):
    """Sell shares."""
    global account
    if account is None:
        return "Error: No account exists. Please create an account first."
    try:
        price = get_share_price(symbol)
        if price == 0.0:
            return f"Error: Unknown symbol '{symbol}'"
        
        success = account.sell_shares(symbol, quantity)
        if success:
            total_proceeds = price * quantity
            return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f}/share. Total proceeds: ${total_proceeds:.2f}. New balance: ${account.balance:.2f}"
        else:
            current_holding = account.portfolio.get(symbol, 0)
            return f"Error: Insufficient shares. You have {current_holding} shares of {symbol}"
    except Exception as e:
        return f"Error: {str(e)}"

def show_balance():
    """Show current cash balance."""
    global account
    if account is None:
        return "No account exists. Please create an account first."
    return f"Current cash balance: ${account.balance:.2f}"

def show_holdings():
    """Show current holdings."""
    global account
    if account is None:
        return "No account exists. Please create an account first."
    
    holdings = account.report_holdings()
    if not holdings:
        return "No holdings currently."
    
    result = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        result += f"  {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    
    portfolio_value = account.calculate_portfolio_value()
    result += f"\nTotal Portfolio Value: ${portfolio_value:.2f}"
    return result

def show_portfolio_summary():
    """Show complete portfolio summary."""
    global account
    if account is None:
        return "No account exists. Please create an account first."
    
    cash_balance = account.balance
    portfolio_value = account.calculate_portfolio_value()
    total_value = cash_balance + portfolio_value
    profit_loss = account.calculate_profit_loss()
    
    result = f"Portfolio Summary\n"
    result += f"==================\n"
    result += f"Cash Balance: ${cash_balance:.2f}\n"
    result += f"Portfolio Value: ${portfolio_value:.2f}\n"
    result += f"Total Value: ${total_value:.2f}\n"
    result += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    result += f"Profit/Loss: ${profit_loss:.2f} ({'+' if profit_loss >= 0 else ''}{(profit_loss/account.initial_deposit*100):.2f}%)\n"
    
    return result

def show_transactions():
    """Show transaction history."""
    global account
    if account is None:
        return "No account exists. Please create an account first."
    
    transactions = account.report_transactions()
    if not transactions:
        return "No transactions yet."
    
    result = "Transaction History:\n"
    result += "=" * 80 + "\n"
    for i, txn in enumerate(transactions, 1):
        result += f"{i}. {txn['type'].upper()} - {txn['timestamp']}\n"
        
        if txn['type'] == 'deposit':
            result += f"   Amount: ${txn['amount']:.2f}\n"
        elif txn['type'] == 'withdrawal':
            result += f"   Amount: ${txn['amount']:.2f}\n"
        elif txn['type'] == 'buy':
            result += f"   Symbol: {txn['symbol']}, Quantity: {txn['quantity']}, Price: ${txn['price_per_share']:.2f}, Total: ${txn['total_cost']:.2f}\n"
        elif txn['type'] == 'sell':
            result += f"   Symbol: {txn['symbol']}, Quantity: {txn['quantity']}, Price: ${txn['price_per_share']:.2f}, Total: ${txn['total_proceeds']:.2f}\n"
        
        result += f"   Balance After: ${txn['balance_after']:.2f}\n\n"
    
    return result

def show_stock_prices():
    """Display current stock prices."""
    result = "Current Stock Prices:\n"
    result += "====================\n"
    for symbol in ['AAPL', 'TSLA', 'GOOGL']:
        price = get_share_price(symbol)
        result += f"{symbol}: ${price:.2f}\n"
    return result

# Create Gradio interface
with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("A simple account management system for trading simulation")
    
    with gr.Tab("Account Setup"):
        gr.Markdown("## Create Account")
        with gr.Row():
            account_id_input = gr.Textbox(label="Account ID", placeholder="Enter account ID")
            initial_deposit_input = gr.Number(label="Initial Deposit ($)", value=10000)
        create_btn = gr.Button("Create Account")
        create_output = gr.Textbox(label="Result", lines=2)
        create_btn.click(create_account, inputs=[account_id_input, initial_deposit_input], outputs=create_output)
    
    with gr.Tab("Funds Management"):
        gr.Markdown("## Deposit / Withdraw Funds")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Deposit")
                deposit_amount = gr.Number(label="Amount ($)", value=1000)
                deposit_btn = gr.Button("Deposit")
                deposit_output = gr.Textbox(label="Result", lines=2)
                deposit_btn.click(deposit_funds, inputs=deposit_amount, outputs=deposit_output)
            
            with gr.Column():
                gr.Markdown("### Withdraw")
                withdraw_amount = gr.Number(label="Amount ($)", value=500)
                withdraw_btn = gr.Button("Withdraw")
                withdraw_output = gr.Textbox(label="Result", lines=2)
                withdraw_btn.click(withdraw_funds, inputs=withdraw_amount, outputs=withdraw_output)
    
    with gr.Tab("Trading"):
        gr.Markdown("## Buy / Sell Shares")
        gr.Markdown("Available symbols: AAPL, TSLA, GOOGL")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Buy Shares")
                buy_symbol = gr.Textbox(label="Symbol", placeholder="e.g., AAPL")
                buy_quantity = gr.Number(label="Quantity", value=10, precision=0)
                buy_btn = gr.Button("Buy")
                buy_output = gr.Textbox(label="Result", lines=3)
                buy_btn.click(buy_shares_ui, inputs=[buy_symbol, buy_quantity], outputs=buy_output)
            
            with gr.Column():
                gr.Markdown("### Sell Shares")
                sell_symbol = gr.Textbox(label="Symbol", placeholder="e.g., AAPL")
                sell_quantity = gr.Number(label="Quantity", value=5, precision=0)
                sell_btn = gr.Button("Sell")
                sell_output = gr.Textbox(label="Result", lines=3)
                sell_btn.click(sell_shares_ui, inputs=[sell_symbol, sell_quantity], outputs=sell_output)
        
        with gr.Row():
            prices_btn = gr.Button("Show Current Stock Prices")
            prices_output = gr.Textbox(label="Stock Prices", lines=5)
            prices_btn.click(show_stock_prices, outputs=prices_output)
    
    with gr.Tab("Portfolio & Reports"):
        gr.Markdown("## Account Information")
        
        with gr.Row():
            balance_btn = gr.Button("Show Cash Balance")
            balance_output = gr.Textbox(label="Cash Balance", lines=2)
            balance_btn.click(show_balance, outputs=balance_output)
        
        with gr.Row():
            holdings_btn = gr.Button("Show Holdings")
            holdings_output = gr.Textbox(label="Holdings", lines=10)
            holdings_btn.click(show_holdings, outputs=holdings_output)
        
        with gr.Row():
            summary_btn = gr.Button("Show Portfolio Summary")
            summary_output = gr.Textbox(label="Portfolio Summary", lines=10)
            summary_btn.click(show_portfolio_summary, outputs=summary_output)
        
        with gr.Row():
            transactions_btn = gr.Button("Show Transaction History")
            transactions_output = gr.Textbox(label="Transactions", lines=15)
            transactions_btn.click(show_transactions, outputs=transactions_output)

if __name__ == "__main__":
    demo.launch()
