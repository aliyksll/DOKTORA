import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
import yfinance as yf
from scipy import stats

# .env dosyasını yükle
load_dotenv()

class PortfolioOptimizer:
    def __init__(self, symbols, start_date=None, end_date=None):
        """
        Portföy optimizasyonu için gerekli parametreleri başlatır.
        
        Args:
            symbols (list): Hisse senedi sembolleri listesi
            start_date (str): Başlangıç tarihi (YYYY-MM-DD formatında)
            end_date (str): Bitiş tarihi (YYYY-MM-DD formatında)
        """
        self.symbols = symbols
        self.start_date = start_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.data = None
        self.returns = None
        self.weights = None
        self.portfolio_value = 1000000  # Varsayılan portföy değeri (1 milyon TL)
        
    def fetch_data(self):
        """Hisse senedi verilerini yfinance kütüphanesi ile çeker ve işler."""
        print("Veriler çekiliyor...")
        
        try:
            # Tüm hisse senetleri için veri çek
            data = {}
            for symbol in self.symbols:
                # BIST hisseleri için .IS ekle
                ticker_symbol = f"{symbol}.IS" if not symbol.endswith('.IS') else symbol
                ticker = yf.Ticker(ticker_symbol)
                df = ticker.history(start=self.start_date, end=self.end_date)
                if not df.empty:
                    data[symbol] = df['Close']
                else:
                    print(f"Uyarı: {symbol} için veri çekilemedi!")
            
            if not data:
                raise Exception("Hiçbir hisse senedi için veri çekilemedi!")
            
            # Verileri DataFrame'e dönüştür
            self.data = pd.DataFrame(data)
            
            # Verileri CSV dosyasına kaydet
            csv_filename = f"hisse_verileri_{self.start_date}_{self.end_date}.csv"
            self.data.to_csv(csv_filename)
            print(f"\nVeriler {csv_filename} dosyasına kaydedildi")
            
            print(f"\nToplam {len(self.data.columns)} hisse senedi için veri çekildi")
            print(f"Veri aralığı: {self.data.index[0].strftime('%Y-%m-%d')} - {self.data.index[-1].strftime('%Y-%m-%d')}")
            
            # Getirileri hesapla
            self.returns = self.data.pct_change().dropna()
            
        except Exception as e:
            raise Exception(f"Veri çekme hatası: {str(e)}")
        
    def calculate_portfolio_metrics(self, weights):
        """
        Verilen ağırlıklar için portföy metriklerini hesaplar.
        
        Args:
            weights (array): Hisse senedi ağırlıkları
            
        Returns:
            tuple: (getiri, risk, sharpe oranı)
        """
        returns = np.sum(self.returns.mean() * weights) * 252  # Yıllık getiri
        risk = np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() * 252, weights)))  # Yıllık risk
        sharpe = returns / risk if risk != 0 else 0
        return returns, risk, sharpe
    
    def optimize_portfolio(self):
        """Optimal portföy ağırlıklarını hesaplar."""
        print("Portföy optimize ediliyor...")
        
        # Kısıtlamalar
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Ağırlıklar toplamı 1 olmalı
            {'type': 'ineq', 'fun': lambda x: x}  # Ağırlıklar pozitif olmalı
        )
        
        # Başlangıç ağırlıkları (eşit dağılım)
        init_weights = np.array([1/len(self.symbols)] * len(self.symbols))
        
        # Optimizasyon
        result = minimize(
            lambda x: -self.calculate_portfolio_metrics(x)[2],  # Sharpe oranını maksimize et
            init_weights,
            method='SLSQP',
            constraints=constraints,
            bounds=tuple((0, 1) for _ in range(len(self.symbols)))
        )
        
        self.weights = result.x
        return self.weights
    
    def plot_efficient_frontier(self, num_portfolios=1000):
        """Etkin sınır grafiğini çizer."""
        print("Etkin sınır grafiği oluşturuluyor...")
        
        returns_list = []
        risks_list = []
        weights_list = []
        
        for _ in range(num_portfolios):
            weights = np.random.random(len(self.symbols))
            weights = weights / np.sum(weights)
            weights_list.append(weights)
            
            returns, risk, _ = self.calculate_portfolio_metrics(weights)
            returns_list.append(returns)
            risks_list.append(risk)
        
        # Optimal portföy noktası
        opt_returns, opt_risk, _ = self.calculate_portfolio_metrics(self.weights)
        
        # Grafik
        plt.figure(figsize=(10, 6))
        plt.scatter(risks_list, returns_list, c='blue', alpha=0.5)
        plt.scatter(opt_risk, opt_returns, c='red', marker='*', s=200, label='Optimal Portföy')
        plt.xlabel('Risk (Volatilite)')
        plt.ylabel('Beklenen Getiri')
        plt.title('Etkin Sınır ve Optimal Portföy')
        plt.legend()
        plt.grid(True)
        plt.savefig('efficient_frontier.png')
        plt.close()
        
    def plot_portfolio_composition(self):
        """Portföy bileşimini gösteren pasta grafiği çizer."""
        plt.figure(figsize=(10, 6))
        plt.pie(self.weights, labels=self.symbols, autopct='%1.1f%%')
        plt.title('Optimal Portföy Bileşimi')
        plt.savefig('portfolio_composition.png')
        plt.close()
        
    def calculate_var(self, confidence_level=0.95, time_horizon=1):
        """
        Value at Risk (VaR) değerini hesaplar.
        
        Args:
            confidence_level (float): Güven seviyesi (varsayılan: 0.95)
            time_horizon (int): Zaman ufku (gün cinsinden, varsayılan: 1)
            
        Returns:
            float: VaR değeri
        """
        if self.weights is None:
            raise Exception("Önce portföyü optimize edin!")
            
        # Portföy getirilerini hesapla
        portfolio_returns = np.sum(self.returns * self.weights, axis=1)
        
        # VaR hesaplama (normal dağılım varsayımı ile)
        var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        
        # Günlük VaR'ı yıllık VaR'a çevir
        annual_var = var * np.sqrt(252)
        
        # TL cinsinden VaR
        var_amount = self.portfolio_value * annual_var
        
        return var_amount
    
    def calculate_cvar(self, confidence_level=0.95, time_horizon=1):
        """
        Conditional Value at Risk (CVaR) değerini hesaplar.
        
        Args:
            confidence_level (float): Güven seviyesi (varsayılan: 0.95)
            time_horizon (int): Zaman ufku (gün cinsinden, varsayılan: 1)
            
        Returns:
            float: CVaR değeri
        """
        if self.weights is None:
            raise Exception("Önce portföyü optimize edin!")
            
        # Portföy getirilerini hesapla
        portfolio_returns = np.sum(self.returns * self.weights, axis=1)
        
        # VaR değerini hesapla
        var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        
        # CVaR hesaplama
        cvar = portfolio_returns[portfolio_returns <= var].mean()
        
        # Günlük CVaR'ı yıllık CVaR'a çevir
        annual_cvar = cvar * np.sqrt(252)
        
        # TL cinsinden CVaR
        cvar_amount = self.portfolio_value * annual_cvar
        
        return cvar_amount
    
    def generate_report(self):
        """Portföy optimizasyonu raporu oluşturur."""
        if self.weights is None:
            print("Önce portföyü optimize edin!")
            return
            
        returns, risk, sharpe = self.calculate_portfolio_metrics(self.weights)
        
        # VaR ve CVaR hesapla
        var_95 = self.calculate_var(confidence_level=0.95)
        var_99 = self.calculate_var(confidence_level=0.99)
        cvar_95 = self.calculate_cvar(confidence_level=0.95)
        cvar_99 = self.calculate_cvar(confidence_level=0.99)
        
        report = f"""
        Portföy Optimizasyon Raporu
        ==========================
        
        Tarih Aralığı: {self.start_date} - {self.end_date}
        Portföy Değeri: {self.portfolio_value:,.2f} TL
        
        Optimal Portföy Ağırlıkları:
        ---------------------------
        """
        
        for symbol, weight in zip(self.symbols, self.weights):
            report += f"{symbol}: {weight:.2%}\n"
            
        report += f"""
        
        Portföy Metrikleri:
        ------------------
        Yıllık Beklenen Getiri: {returns:.2%}
        Yıllık Risk (Volatilite): {risk:.2%}
        Sharpe Oranı: {sharpe:.2f}
        
        Risk Metrikleri:
        --------------
        %95 Güven Seviyesi VaR: {var_95:,.2f} TL
        %99 Güven Seviyesi VaR: {var_99:,.2f} TL
        %95 Güven Seviyesi CVaR: {cvar_95:,.2f} TL
        %99 Güven Seviyesi CVaR: {cvar_99:,.2f} TL
        """
        
        with open('portfolio_report.txt', 'w') as f:
            f.write(report)
            
        print("Rapor oluşturuldu: portfolio_report.txt")

def main():
    # Örnek kullanım
    symbols = ['THYAO', 'GARAN', 'ASELS', 'EREGL', 'KCHOL']  # BIST hisseleri
    start_date = '2023-01-01'  # 1 Ocak 2023
    optimizer = PortfolioOptimizer(symbols, start_date=start_date)
    
    try:
        # Verileri çek
        optimizer.fetch_data()
        
        # Portföyü optimize et
        optimizer.optimize_portfolio()
        
        # Grafikleri oluştur
        optimizer.plot_efficient_frontier()
        optimizer.plot_portfolio_composition()
        
        # Rapor oluştur
        optimizer.generate_report()
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 