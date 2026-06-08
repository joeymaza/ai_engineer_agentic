import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from accounts import Account, get_share_price


class TestGetSharePrice(unittest.TestCase):
    def test_known_symbol(self):
        self.assertEqual(get_share_price('AAPL'), 150.00)
        self.assertEqual(get_share_price('TSLA'), 650.00)
        self.assertEqual(get_share_price('GOOGL'), 2800.00)

    def test_unknown_symbol(self):
        self.assertEqual(get_share_price('MSFT'), 0.0)
        self.assertEqual(get_share_price(''), 0.0)
        self.assertEqual(get_share_price('NONEXISTENT'), 0.0)

    def test_case_sensitivity(self):
        self.assertEqual(get_share_price('aapl'), 0.0)
        self.assertEqual(get_share_price('tsla'), 0.0)


class TestAccountInitialization(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC001', 1000.0)

    def test_initialization(self):
        self.assertEqual(self.account.account_id, 'ACC001')
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(len(self.account.transaction_history), 1)

    def test_initial_transaction_record(self):
        transaction = self.account.transaction_history[0]
        self.assertEqual(transaction['type'], 'deposit')
        self.assertEqual(transaction['amount'], 1000.0)
        self.assertEqual(transaction['balance_after'], 1000.0)
        self.assertIn('timestamp', transaction)


class TestAccountDeposit(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC002', 500.0)

    def test_deposit_positive_amount(self):
        self.account.deposit(200.0)
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(len(self.account.transaction_history), 2)
        transaction = self.account.transaction_history[-1]
        self.assertEqual(transaction['type'], 'deposit')
        self.assertEqual(transaction['amount'], 200.0)
        self.assertEqual(transaction['balance_after'], 700.0)

    def test_deposit_zero_amount_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            self.account.deposit(0)
        self.assertEqual(str(context.exception), "Deposit amount must be positive")

    def test_deposit_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            self.account.deposit(-100.0)
        self.assertEqual(str(context.exception), "Deposit amount must be positive")

    def test_deposit_multiple_times(self):
        self.account.deposit(100.0)
        self.account.deposit(50.0)
        self.assertEqual(self.account.balance, 650.0)
        self.assertEqual(len(self.account.transaction_history), 3)


class TestAccountWithdraw(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC003', 1000.0)

    def test_withdraw_sufficient_funds(self):
        result = self.account.withdraw(300.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(len(self.account.transaction_history), 2)
        transaction = self.account.transaction_history[-1]
        self.assertEqual(transaction['type'], 'withdrawal')
        self.assertEqual(transaction['amount'], 300.0)
        self.assertEqual(transaction['balance_after'], 700.0)

    def test_withdraw_exact_balance(self):
        result = self.account.withdraw(1000.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 0.0)

    def test_withdraw_insufficient_funds(self):
        result = self.account.withdraw(1500.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(len(self.account.transaction_history), 1)

    def test_withdraw_zero_amount(self):
        result = self.account.withdraw(0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)

    def test_withdraw_negative_amount(self):
        result = self.account.withdraw(-100.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)


class TestAccountBuyShares(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC004', 10000.0)

    def test_buy_shares_success(self):
        result = self.account.buy_shares('AAPL', 10)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 10000.0 - 10 * 150.0)
        self.assertEqual(self.account.portfolio['AAPL'], 10)
        self.assertEqual(len(self.account.transaction_history), 2)
        transaction = self.account.transaction_history[-1]
        self.assertEqual(transaction['type'], 'buy')
        self.assertEqual(transaction['symbol'], 'AAPL')
        self.assertEqual(transaction['quantity'], 10)
        self.assertEqual(transaction['price_per_share'], 150.0)
        self.assertEqual(transaction['total_cost'], 1500.0)

    def test_buy_shares_insufficient_balance(self):
        result = self.account.buy_shares('TSLA', 20)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 10000.0)
        self.assertNotIn('TSLA', self.account.portfolio)

    def test_buy_shares_exact_balance(self):
        result = self.account.buy_shares('GOOGL', 3)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 10000.0 - 3 * 2800.0)  # 8400
        self.assertEqual(self.account.portfolio['GOOGL'], 3)

    def test_buy_shares_zero_quantity(self):
        result = self.account.buy_shares('AAPL', 0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 10000.0)

    def test_buy_shares_negative_quantity(self):
        result = self.account.buy_shares('AAPL', -5)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 10000.0)

    def test_buy_shares_unknown_symbol(self):
        result = self.account.buy_shares('MSFT', 10)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 10000.0)

    def test_buy_multiple_times_same_symbol(self):
        self.account.buy_shares('AAPL', 5)
        self.account.buy_shares('AAPL', 10)
        self.assertEqual(self.account.portfolio['AAPL'], 15)
        total_cost = 5 * 150.0 + 10 * 150.0
        self.assertEqual(self.account.balance, 10000.0 - total_cost)

    def test_buy_multiple_symbols(self):
        self.account.buy_shares('AAPL', 5)
        self.account.buy_shares('TSLA', 5)
        self.assertEqual(self.account.portfolio['AAPL'], 5)
        self.assertEqual(self.account.portfolio['TSLA'], 5)
        total_cost = 5 * 150.0 + 5 * 650.0
        self.assertEqual(self.account.balance, 10000.0 - total_cost)


class TestAccountSellShares(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC005', 10000.0)
        self.account.buy_shares('AAPL', 20)
        self.account.buy_shares('TSLA', 5)

    def test_sell_shares_success(self):
        result = self.account.sell_shares('AAPL', 10)
        self.assertTrue(result)
        self.assertEqual(self.account.portfolio['AAPL'], 10)
        self.assertEqual(self.account.balance, 10000.0 - 20 * 150.0 + 10 * 150.0)
        self.assertEqual(len(self.account.transaction_history), 4)
        transaction = self.account.transaction_history[-1]
        self.assertEqual(transaction['type'], 'sell')
        self.assertEqual(transaction['symbol'], 'AAPL')
        self.assertEqual(transaction['quantity'], 10)
        self.assertEqual(transaction['price_per_share'], 150.0)
        self.assertEqual(transaction['total_proceeds'], 1500.0)

    def test_sell_all_shares(self):
        result = self.account.sell_shares('AAPL', 20)
        self.assertTrue(result)
        self.assertNotIn('AAPL', self.account.portfolio)
        self.assertEqual(self.account.balance, 10000.0)  # original balance after buying and selling at same price

    def test_sell_shares_insufficient_shares(self):
        result = self.account.sell_shares('AAPL', 30)
        self.assertFalse(result)
        self.assertEqual(self.account.portfolio['AAPL'], 20)
        self.assertEqual(self.account.balance, 10000.0 - 20 * 150.0 - 5 * 650.0)

    def test_sell_shares_not_owned(self):
        result = self.account.sell_shares('GOOGL', 5)
        self.assertFalse(result)

    def test_sell_shares_zero_quantity(self):
        result = self.account.sell_shares('AAPL', 0)
        self.assertFalse(result)

    def test_sell_shares_negative_quantity(self):
        result = self.account.sell_shares('AAPL', -5)
        self.assertFalse(result)

    def test_sell_shares_unknown_symbol(self):
        result = self.account.sell_shares('MSFT', 5)
        self.assertFalse(result)

    def test_sell_profits_add_to_balance(self):
        initial_balance = self.account.balance
        self.account.sell_shares('AAPL', 5)
        expected_balance = initial_balance + 5 * 150.0
        self.assertEqual(self.account.balance, expected_balance)


class TestAccountPortfolioValue(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC006', 10000.0)
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('TSLA', 5)

    def test_calculate_portfolio_value(self):
        expected_value = 10 * 150.0 + 5 * 650.0
        self.assertEqual(self.account.calculate_portfolio_value(), expected_value)

    def test_empty_portfolio_value(self):
        empty_account = Account('ACC007', 500.0)
        self.assertEqual(empty_account.calculate_portfolio_value(), 0.0)

    def test_portfolio_value_after_partial_sell(self):
        self.account.sell_shares('AAPL', 3)
        expected_value = 7 * 150.0 + 5 * 650.0
        self.assertEqual(self.account.calculate_portfolio_value(), expected_value)


class TestAccountProfitLoss(unittest.TestCase):
    def test_no_trades_no_change(self):
        account = Account('ACC008', 1000.0)
        self.assertEqual(account.calculate_profit_loss(), 0.0)

    def test_loss_from_buying(self):
        account = Account('ACC009', 10000.0)
        account.buy_shares('AAPL', 10)
        # Balance: 10000 - 1500 = 8500, Portfolio value: 1500, Total: 10000 -> Profit/Loss: 0
        expected_loss = account.balance + account.calculate_portfolio_value() - account.initial_deposit
        self.assertEqual(account.calculate_profit_loss(), expected_loss)

    def test_profit_after_deposit(self):
        account = Account('ACC010', 1000.0)
        account.deposit(500.0)
        # Initial: 1000, After deposit: balance 1500, no portfolio, total = 1500, profit_loss = 500
        self.assertEqual(account.calculate_profit_loss(), 500.0)

    def test_profit_after_trade(self):
        account = Account('ACC011', 10000.0)
        account.buy_shares('AAPL', 10)
        account.sell_shares('AAPL', 10)
        # After buy and sell at same price, balance returns to 10000, profit = 0
        self.assertEqual(account.calculate_profit_loss(), 0.0)


class TestAccountReports(unittest.TestCase):
    def setUp(self):
        self.account = Account('ACC012', 10000.0)
        self.account.buy_shares('AAPL', 15)
        self.account.buy_shares('TSLA', 3)
        self.account.sell_shares('AAPL', 5)

    def test_report_holdings(self):
        holdings = self.account.report_holdings()
        self.assertEqual(holdings, {'AAPL': 10, 'TSLA': 3})
        # Ensure it's a copy, not reference
        holdings['AAPL'] = 0
        self.assertEqual(self.account.portfolio['AAPL'], 10)

    def test_report_transactions(self):
        transactions = self.account.report_transactions()
        self.assertEqual(len(transactions), 4)  # initial deposit + buy + buy + sell
        self.assertEqual(transactions[0]['type'], 'deposit')
        self.assertEqual(transactions[1]['type'], 'buy')
        self.assertEqual(transactions[2]['type'], 'buy')
        self.assertEqual(transactions[3]['type'], 'sell')
        # Ensure it's a copy
        transactions.append({'extra': 'test'})
        self.assertEqual(len(self.account.transaction_history), 4)

    def test_report_transactions_empty_initial(self):
        account = Account('ACC013', 500.0)
        transactions = account.report_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['type'], 'deposit')


if __name__ == '__main__':
    unittest.main()