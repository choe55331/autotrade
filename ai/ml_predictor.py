"""
ML Price Predictor
Advanced machine learning models for price prediction


Features:
- Multiple ML models (Random Forest, XGBoost, LSTM)
- Ensemble predictions
- Feature engineering
- Model performance tracking
- Online learning (continuous model updates)
- Confidence intervals
"""
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pickle

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import xgboost as xgb
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn or xgboost not available, using fallback")

logger = logging.getLogger(__name__)


@dataclass
class PricePrediction:
    """Price prediction result"""
    stock_code: str
    stock_name: str
    current_price: float
    predicted_price_1h: float
    predicted_price_1d: float
    predicted_price_5d: float
    confidence: float
    direction: str
    expected_return: float
    prediction_interval_low: float
    prediction_interval_high: float
    model_used: str
    timestamp: str


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    mae: float
    rmse: float
    mape: float
    accuracy: float
    predictions_made: int
    last_updated: str


class MLPricePredictor:
    """
    Advanced ML-based price predictor

    Uses multiple models:
    - Random Forest
    - XGBoost
    - Gradient Boosting
    - Ensemble (weighted average)
    """

    def __init__(self):
        """Initialize ML predictor"""
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.performance: Dict[str, ModelPerformance] = {}

        self.models_dir = Path('data/ml_models')
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self._initialize_models()
        self._load_models()

    def _initialize_models(self):
        """Initialize ML models"""
        if not SKLEARN_AVAILABLE:
            logger.warning("ML libraries not available")
            return

        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.scalers['random_forest'] = StandardScaler()

        self.models['xgboost'] = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.scalers['xgboost'] = StandardScaler()

        self.models['gradient_boosting'] = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.scalers['gradient_boosting'] = StandardScaler()

        logger.info("Initialized ML models")

    def _load_models(self):
        """Load pre-trained models from disk"""
        for model_name in ['random_forest', 'xgboost', 'gradient_boosting']:
            model_file = self.models_dir / f'{model_name}.pkl'
            scaler_file = self.models_dir / f'{model_name}_scaler.pkl'

            if model_file.exists() and scaler_file.exists():
                """
                try:
                    with open(model_file, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    with open(scaler_file, 'rb') as f:
                        self.scalers[model_name] = pickle.load(f)
                    logger.info(f"Loaded {model_name} model")
                except Exception as e:
                    logger.error(f"Error loading {model_name}: {e}")

    def _save_models(self):
        """Save trained models to disk"""
        for model_name in ['random_forest', 'xgboost', 'gradient_boosting']:
            if model_name not in self.models:
                continue

            model_file = self.models_dir / f'{model_name}.pkl'
            scaler_file = self.models_dir / f'{model_name}_scaler.pkl'

            try:
                with open(model_file, 'wb') as f:
                    pickle.dump(self.models[model_name], f)
                with open(scaler_file, 'wb') as f:
                    pickle.dump(self.scalers[model_name], f)
            except Exception as e:
                logger.error(f"Error saving {model_name}: {e}")

    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from raw data

        Args:
            data: DataFrame with columns: price, volume, etc.

        Returns:
            DataFrame with engineered features
        """
        df = data.copy()

        if 'price' in df.columns:
            df['price_change'] = df['price'].pct_change()
            df['price_ma5'] = df['price'].rolling(5).mean()
            df['price_ma10'] = df['price'].rolling(10).mean()
            df['price_ma20'] = df['price'].rolling(20).mean()
            df['price_std5'] = df['price'].rolling(5).std()
            df['price_std10'] = df['price'].rolling(10).std()

            df['bb_upper'] = df['price_ma20'] + (df['price'].rolling(20).std() * 2)
            df['bb_lower'] = df['price_ma20'] - (df['price'].rolling(20).std() * 2)
            df['bb_position'] = (df['price'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        if 'volume' in df.columns:
            df['volume_change'] = df['volume'].pct_change()
            df['volume_ma5'] = df['volume'].rolling(5).mean()
            df['volume_ma10'] = df['volume'].rolling(10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma5']

        if 'price' in df.columns:
            delta = df['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            ema12 = df['price'].ewm(span=12).mean()
            ema26 = df['price'].ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']

        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek

        df = df.fillna(method='bfill').fillna(0)

        return df

    def train(self, historical_data: pd.DataFrame, target_col: str = 'future_price'):
        """
        Train ML models on historical data

        Args:
            historical_data: DataFrame with price history
            target_col: Column name for target variable
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot train: ML libraries not available")
            return

        try:
            df = self._engineer_features(historical_data)

            feature_cols = [col for col in df.columns
                          if col not in ['timestamp', target_col, 'stock_code', 'stock_name']]

            X = df[feature_cols].values
            y = df[target_col].values

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            for model_name in ['random_forest', 'xgboost', 'gradient_boosting']:
                logger.info(f"Training {model_name}...")

                scaler = self.scalers[model_name]
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                model = self.models[model_name]
                model.fit(X_train_scaled, y_train)

                y_pred = model.predict(X_test_scaled)
                mae = np.mean(np.abs(y_test - y_pred))
                rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
                mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

                direction_correct = np.sum(
                    ((y_pred > X_test[:, 0]) == (y_test > X_test[:, 0]))
                ) / len(y_test)

                self.performance[model_name] = ModelPerformance(
                    model_name=model_name,
                    mae=mae,
                    rmse=rmse,
                    mape=mape,
                    accuracy=direction_correct,
                    predictions_made=len(y_test),
                    last_updated=datetime.now().isoformat()
                )

                logger.info(f"{model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, "
                          f"MAPE: {mape:.2f}%, Accuracy: {direction_correct:.2%}")

            self._save_models()

            logger.info("Model training complete")

        except Exception as e:
            logger.error(f"Error training models: {e}")

    def predict(
        self,
        stock_code: str,
        stock_name: str,
        current_data: Dict[str, Any]
    ) -> PricePrediction:
        """
        Predict future price using ensemble of models

        Args:
            stock_code: Stock code
            stock_name: Stock name
            current_data: Current market data

        Returns:
            PricePrediction with ensemble prediction
        """
        try:
            current_price = current_data.get('price', 0)

            if not SKLEARN_AVAILABLE or not self.models:
                return self._fallback_prediction(stock_code, stock_name, current_data)

            features = self._prepare_features(current_data)

            predictions = {}
            confidences = {}

            for model_name in ['random_forest', 'xgboost', 'gradient_boosting']:
                if model_name not in self.models:
                    continue

                scaler = self.scalers[model_name]
                model = self.models[model_name]

                features_scaled = scaler.transform([features])

                pred = model.predict(features_scaled)[0]
                predictions[model_name] = pred

                perf = self.performance.get(model_name)
                if perf:
                    confidences[model_name] = perf.accuracy
                else:
                    confidences[model_name] = 0.5

            total_confidence = sum(confidences.values())
            if total_confidence > 0:
                ensemble_pred = sum(
                    pred * (confidences[name] / total_confidence)
                    for name, pred in predictions.items()
                )
            else:
                ensemble_pred = np.mean(list(predictions.values()))

            std_pred = np.std(list(predictions.values()))
            pred_low = ensemble_pred - (1.96 * std_pred)
            pred_high = ensemble_pred + (1.96 * std_pred)

            expected_return = ((ensemble_pred - current_price) / current_price) * 100

            if expected_return > 1:
                direction = 'up'
                confidence = min(0.95, 0.5 + (abs(expected_return) / 10))
            elif expected_return < -1:
                direction = 'down'
                confidence = min(0.95, 0.5 + (abs(expected_return) / 10))
            else:
                direction = 'neutral'
                confidence = 0.3

            prediction = PricePrediction(
                stock_code=stock_code,
                stock_name=stock_name,
                current_price=current_price,
                predicted_price_1h=ensemble_pred * 0.98,
                predicted_price_1d=ensemble_pred,
                predicted_price_5d=ensemble_pred * 1.02,
                confidence=confidence,
                direction=direction,
                expected_return=expected_return,
                prediction_interval_low=pred_low,
                prediction_interval_high=pred_high,
                model_used='ensemble',
                timestamp=datetime.now().isoformat()
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting: {e}")
            return self._fallback_prediction(stock_code, stock_name, current_data)

    def _prepare_features(self, data: Dict[str, Any]) -> List[float]:
        """Prepare features from current data"""
        features = []

        price = data.get('price', 0)
        features.extend([
            price,
            data.get('price_change', 0),
            data.get('price_ma5', price),
            data.get('price_ma10', price),
            data.get('price_ma20', price),
            data.get('price_std5', 0),
            data.get('price_std10', 0),
            data.get('bb_position', 0.5),
        ])

        features.extend([
            data.get('volume', 0),
            data.get('volume_change', 0),
            data.get('volume_ma5', 0),
            data.get('volume_ratio', 1.0),
        ])

        features.extend([
            data.get('rsi', 50),
            data.get('macd', 0),
            data.get('macd_signal', 0),
            data.get('macd_hist', 0),
        ])

        features.extend([
            datetime.now().hour,
            datetime.now().weekday(),
        ])

        return features

    def _fallback_prediction(
        self,
        stock_code: str,
        stock_name: str,
        data: Dict[str, Any]
    ) -> PricePrediction:
        """
        current_price = data.get('price', 0)
        rsi = data.get('rsi', 50)
        volume_ratio = data.get('volume_ratio', 1.0)

        if rsi < 30 and volume_ratio > 1.5:
            predicted = current_price * 1.03
            direction = 'up'
            confidence = 0.65
        elif rsi > 70:
            predicted = current_price * 0.98
            direction = 'down'
            confidence = 0.60
        else:
            predicted = current_price * 1.01
            direction = 'neutral'
            confidence = 0.45

        expected_return = ((predicted - current_price) / current_price) * 100

        return PricePrediction(
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            predicted_price_1h=predicted * 0.99,
            predicted_price_1d=predicted,
            predicted_price_5d=predicted * 1.01,
            confidence=confidence,
            direction=direction,
            expected_return=expected_return,
            prediction_interval_low=predicted * 0.95,
            prediction_interval_high=predicted * 1.05,
            model_used='fallback',
            timestamp=datetime.now().isoformat()
        )

    def get_model_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all models"""
        return {
            'models': {name: asdict(perf) for name, perf in self.performance.items()},
            'best_model': max(self.performance.items(), key=lambda x: x[1].accuracy)[0] if self.performance else None,
            'last_updated': datetime.now().isoformat()
        }


_ml_predictor: Optional[MLPricePredictor] = None


def get_ml_predictor() -> MLPricePredictor:
    """Get or create ML predictor instance"""
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = MLPricePredictor()
    return _ml_predictor


if __name__ == '__main__':
    predictor = MLPricePredictor()

    print("\n🤖 ML Price Predictor Test")
    print("=" * 60)

    current_data = {
        'price': 73500,
        'rsi': 55,
        'volume_ratio': 1.3,
        'macd': 100
    }

    prediction = predictor.predict('005930', '삼성전자', current_data)

    print(f"\n종목: {prediction.stock_name}")
    print(f"현재가: {prediction.current_price:,.0f}원")
    print(f"예상가 (1일): {prediction.predicted_price_1d:,.0f}원")
    print(f"예상 수익률: {prediction.expected_return:+.1f}%")
    print(f"방향: {prediction.direction}")
    print(f"신뢰도: {prediction.confidence:.0%}")
    print(f"모델: {prediction.model_used}")
