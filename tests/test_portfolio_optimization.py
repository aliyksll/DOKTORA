import unittest
import pandas as pd
import numpy as np
from portfolio_optimization import PortfolioOptimizer

class TestPortfolioOptimizer(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak metod"""
        self.symbols = ['THYAO', 'GARAN', 'ASELS']
        self.start_date = '2023-01-01'
        self.end_date = '2023-12-31'
        self.optimizer = PortfolioOptimizer(self.symbols, self.start_date, self.end_date)
        
    def test_initialization(self):
        """Optimizer'ın doğru başlatıldığını kontrol eder"""
        self.assertEqual(self.optimizer.symbols, self.symbols)
        self.assertEqual(self.optimizer.start_date, self.start_date)
        self.assertEqual(self.optimizer.end_date, self.end_date)
        self.assertIsNone(self.optimizer.data)
        self.assertIsNone(self.optimizer.returns)
        self.assertIsNone(self.optimizer.weights)
        
    def test_fetch_data(self):
        """Veri çekme fonksiyonunu test eder"""
        self.optimizer.fetch_data()
        self.assertIsNotNone(self.optimizer.data)
        self.assertTrue(isinstance(self.optimizer.data, pd.DataFrame))
        self.assertEqual(len(self.optimizer.data.columns), len(self.symbols))
        
    def test_calculate_returns(self):
        """Getiri hesaplama fonksiyonunu test eder"""
        self.optimizer.fetch_data()
        self.optimizer.returns = self.optimizer.data.pct_change().dropna()
        self.assertIsNotNone(self.optimizer.returns)
        self.assertTrue(isinstance(self.optimizer.returns, pd.DataFrame))
        
    def test_portfolio_metrics(self):
        """Portföy metriklerinin hesaplanmasını test eder"""
        self.optimizer.fetch_data()
        self.optimizer.returns = self.optimizer.data.pct_change().dropna()
        weights = np.array([0.4, 0.3, 0.3])
        returns, risk, sharpe = self.optimizer.calculate_portfolio_metrics(weights)
        self.assertTrue(isinstance(returns, float))
        self.assertTrue(isinstance(risk, float))
        self.assertTrue(isinstance(sharpe, float))
        
    def test_optimize_portfolio(self):
        """Portföy optimizasyonunu test eder"""
        self.optimizer.fetch_data()
        self.optimizer.returns = self.optimizer.data.pct_change().dropna()
        self.optimizer.optimize_portfolio()
        self.assertIsNotNone(self.optimizer.weights)
        self.assertEqual(len(self.optimizer.weights), len(self.symbols))
        self.assertAlmostEqual(sum(self.optimizer.weights), 1.0)
        
    def test_var_calculation(self):
        """VaR hesaplamasını test eder"""
        self.optimizer.fetch_data()
        self.optimizer.returns = self.optimizer.data.pct_change().dropna()
        self.optimizer.weights = np.array([0.4, 0.3, 0.3])
        var = self.optimizer.calculate_var(confidence_level=0.95)
        self.assertTrue(isinstance(var, float))
        self.assertLess(var, 0)  # VaR negatif olmalı
        
    def test_cvar_calculation(self):
        """CVaR hesaplamasını test eder"""
        self.optimizer.fetch_data()
        self.optimizer.returns = self.optimizer.data.pct_change().dropna()
        self.optimizer.weights = np.array([0.4, 0.3, 0.3])
        cvar = self.optimizer.calculate_cvar(confidence_level=0.95)
        self.assertTrue(isinstance(cvar, float))
        self.assertLess(cvar, 0)  # CVaR negatif olmalı

if __name__ == '__main__':
    unittest.main() 