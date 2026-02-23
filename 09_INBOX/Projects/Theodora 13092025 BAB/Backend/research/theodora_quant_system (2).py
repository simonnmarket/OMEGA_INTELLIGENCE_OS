import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
import json
import os

warnings.filterwarnings('ignore')

try:
    import talib as ta
except Exception:
    ta = None


class TheodoraQuantSystem:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []

    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

        if ta is not None:
            df['rsi'] = ta.RSI(df['close'], timeperiod=14)
            macd, macd_signal, _ = ta.MACD(df['close'])
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            bb_u, bb_m, bb_l = ta.BBANDS(df['close'])
            df['bb_upper'] = bb_u
            df['bb_middle'] = bb_m
            df['bb_lower'] = bb_l
            df['atr'] = ta.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            df['adx'] = ta.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            df['obv'] = ta.OBV(df['close'], df['tick_volume'])
        else:
            # Fallbacks simples se talib indisponível
            df['rsi'] = df['returns'].rolling(14).mean()
            df['macd'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            std = df['close'].rolling(20).std()
            ma = df['close'].rolling(20).mean()
            df['bb_upper'] = ma + 2 * std
            df['bb_middle'] = ma
            df['bb_lower'] = ma - 2 * std
            tr = (df['high'] - df['low']).combine_first((df['high'] - df['close'].shift(1)).abs()).combine_first((df['low'] - df['close'].shift(1)).abs())
            df['atr'] = tr.rolling(14).mean()
            df['adx'] = (df['high'] - df['low']).rolling(14).mean()
            df['obv'] = (np.sign(df['close'].diff().fillna(0)) * df['tick_volume']).cumsum()

        df['z_score'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()
        df['momentum'] = df['close'] / df['close'].shift(5) - 1
        df['volume_ratio'] = df['tick_volume'] / df['tick_volume'].rolling(20).mean()
        df['body_size'] = (df['close'] - df['open']).abs() / df['atr']
        df['high_low_ratio'] = (df['high'] - df['low']) / df['atr']

        return df.dropna()

    def prepare_ml_data(self, df: pd.DataFrame, lookback: int = 50):
        features = []
        targets = []

        for i in range(lookback, len(df) - 1):
            window = df.iloc[i - lookback:i]

            bb_range = (window['bb_upper'].iloc[-1] - window['bb_lower'].iloc[-1])
            bb_pos = 0.5 if bb_range == 0 else (window['close'].iloc[-1] - window['bb_lower'].iloc[-1]) / bb_range

            feature_set = {
                'rsi': window['rsi'].iloc[-1],
                'macd_diff': window['macd'].iloc[-1] - window['macd_signal'].iloc[-1],
                'bb_position': bb_pos,
                'volatility': window['volatility'].iloc[-1],
                'adx_strength': window['adx'].iloc[-1],
                'volume_spike': window['volume_ratio'].iloc[-1],
                'momentum': window['momentum'].iloc[-1],
                'z_score': window['z_score'].iloc[-1],
                'skewness': window['returns'].skew(),
                'kurtosis': window['returns'].kurtosis(),
                'hurst': self.calculate_hurst_exponent(window['close'])
            }

            features.append(list(feature_set.values()))
            future_return = df['close'].iloc[i + 1] / df['close'].iloc[i] - 1
            targets.append(1 if future_return > 0 else 0)

        return np.array(features), np.array(targets), list(feature_set.keys())

    def calculate_hurst_exponent(self, prices: pd.Series) -> float:
        lags = range(2, 20)
        tau = [np.sqrt(np.std(np.subtract(prices.values[lag:], prices.values[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(list(lags)), np.log(tau), 1)
        return float(poly[0]) * 2.0

    def train_model(self, symbols, timeframe=mt5.TIMEFRAME_M1, bars=5000):
        all_features = []
        all_targets = []

        for symbol in symbols:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            if rates is None:
                continue
            df = pd.DataFrame(rates)
            df = self.create_advanced_features(df)
            if len(df) > 100:
                features, targets, feature_names = self.prepare_ml_data(df)
                if len(features) > 0:
                    all_features.extend(features)
                    all_targets.extend(targets)

        if not all_features:
            raise ValueError("Dados insuficientes para treinamento")

        self.feature_columns = feature_names
        X = np.array(all_features)
        y = np.array(all_targets)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            class_weight='balanced_subsample',
            random_state=42
        )

        self.model.fit(X_train, y_train)
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        print(f"Modelo treinado - Acurácia: Treino {train_score:.3f}, Teste {test_score:.3f}")
        return True

    def predict_signal(self, symbol, timeframe=mt5.TIMEFRAME_M1):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 120)
        if rates is None:
            return "HOLD", 0.0
        df = pd.DataFrame(rates)
        df = self.create_advanced_features(df)
        if len(df) < 50 or self.model is None:
            return "HOLD", 0.0

        window = df.iloc[-50:]
        bb_range = (window['bb_upper'].iloc[-1] - window['bb_lower'].iloc[-1])
        bb_pos = 0.5 if bb_range == 0 else (window['close'].iloc[-1] - window['bb_lower'].iloc[-1]) / bb_range
        feature_set = [
            window['rsi'].iloc[-1],
            window['macd'].iloc[-1] - window['macd_signal'].iloc[-1],
            bb_pos,
            window['volatility'].iloc[-1],
            window['adx'].iloc[-1],
            window['volume_ratio'].iloc[-1],
            window['momentum'].iloc[-1],
            window['z_score'].iloc[-1],
            window['returns'].skew(),
            window['returns'].kurtosis(),
            self.calculate_hurst_exponent(window['close'])
        ]
        X_current = self.scaler.transform([feature_set])
        proba = self.model.predict_proba(X_current)[0][1]
        pred = 1 if proba >= 0.5 else 0
        return ("BUY" if pred == 1 else "SELL"), float(proba)


def _load_config():
    config_path = os.path.join("Backend", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("THEODORA QUANT SYSTEM - Research")
    cfg = _load_config()
    syms = cfg.get('symbols', ['BTCUSD'])
    if not mt5.initialize():
        print("Falha ao inicializar MT5")
        return
    login_ok = mt5.login(cfg['mt5_account'], cfg['mt5_password'], cfg['mt5_server'])
    if not login_ok:
        print("Falha no login MT5:", mt5.last_error())
        return

    q = TheodoraQuantSystem()
    print("Treinando modelo...")
    q.train_model(syms, timeframe=mt5.TIMEFRAME_M1, bars=3000)
    print("Rodando loop de predição...")
    for s in syms:
        sig, conf = q.predict_signal(s, timeframe=mt5.TIMEFRAME_M1)
        print(f"{s}: {sig} conf={conf:.2f}")

    mt5.shutdown()


if __name__ == '__main__':
    main()


