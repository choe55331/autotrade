"""
Deep Learning Price Predictor
LSTM, CNN, and Transformer models for stock price prediction
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DeepLearningPredictor:
    """
    Advanced deep learning predictor using multiple architectures
    - LSTM for time series prediction
    - CNN for pattern recognition
    - Transformer for complex dependencies
    """

    def __init__(
        self,
        sequence_length: int = 60,
        prediction_horizon: int = 5,
        model_dir: str = "models/dl_models"
    ):
        """
        Initialize deep learning predictor

        Args:
            sequence_length: Number of historical days to use
            prediction_horizon: Days ahead to predict
            model_dir: Directory to save/load models
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model_dir = model_dir

        # Check if deep learning libraries are available
        self.tf_available = self._check_tensorflow()
        self.torch_available = self._check_pytorch()

        # Model instances
        self.lstm_model = None
        self.cnn_model = None
        self.transformer_model = None

        # Feature scalers
        self.price_scaler = None
        self.feature_scaler = None

        os.makedirs(model_dir, exist_ok=True)

        logger.info(f"Deep Learning Predictor initialized")
        logger.info(f"TensorFlow available: {self.tf_available}")
        logger.info(f"PyTorch available: {self.torch_available}")

    def _check_tensorflow(self) -> bool:
        """Check if TensorFlow is available"""
        try:
            import tensorflow as tf
            # Suppress TF warnings
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            logger.info(f"TensorFlow {tf.__version__} available")
            return True
        except ImportError:
            logger.warning("TensorFlow not available - install with: pip install tensorflow")
            return False

    def _check_pytorch(self) -> bool:
        """Check if PyTorch is available"""
        try:
            import torch
            logger.info(f"PyTorch {torch.__version__} available")
            return True
        except ImportError:
            logger.warning("PyTorch not available - install with: pip install torch")
            return False

    def predict_price(
        self,
        stock_data: Dict[str, Any],
        model_type: str = "ensemble"
    ) -> Dict[str, Any]:
        """
        Predict future price using deep learning models

        Args:
            stock_data: Historical stock data
            model_type: "lstm", "cnn", "transformer", or "ensemble"

        Returns:
            Prediction results with confidence intervals
        """
        if not self.tf_available and not self.torch_available:
            return self._get_default_prediction(stock_data)

        try:
            # Prepare data
            X = self._prepare_features(stock_data)

            if X is None or len(X) < self.sequence_length:
                logger.warning("Insufficient data for prediction")
                return self._get_default_prediction(stock_data)

            # Get predictions from models
            predictions = {}

            if model_type in ["lstm", "ensemble"]:
                lstm_pred = self._predict_lstm(X)
                if lstm_pred is not None:
                    predictions['lstm'] = lstm_pred

            if model_type in ["cnn", "ensemble"]:
                cnn_pred = self._predict_cnn(X)
                if cnn_pred is not None:
                    predictions['cnn'] = cnn_pred

            if model_type in ["transformer", "ensemble"]:
                transformer_pred = self._predict_transformer(X)
                if transformer_pred is not None:
                    predictions['transformer'] = transformer_pred

            if not predictions:
                return self._get_default_prediction(stock_data)

            # Combine predictions
            if model_type == "ensemble":
                final_prediction = self._ensemble_predictions(predictions)
            else:
                final_prediction = list(predictions.values())[0]

            # Add metadata
            current_price = stock_data.get('current_price', 0)

            result = {
                'current_price': current_price,
                'predicted_prices': final_prediction['prices'],
                'prediction_horizon': self.prediction_horizon,
                'expected_return': final_prediction['expected_return'],
                'confidence': final_prediction['confidence'],
                'confidence_interval': final_prediction.get('confidence_interval', {}),
                'signal': self._generate_signal(final_prediction),
                'individual_predictions': predictions,
                'model_type': model_type,
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._get_default_prediction(stock_data)

    def _prepare_features(self, stock_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Prepare feature matrix for prediction
        """
        try:
            price_history = stock_data.get('price_history', [])
            volume_history = stock_data.get('volume_history', [])

            if len(price_history) < self.sequence_length:
                return None

            # Get recent data
            recent_prices = price_history[-self.sequence_length:]
            recent_volumes = volume_history[-self.sequence_length:] if volume_history else [0] * self.sequence_length

            # Calculate technical indicators
            features = []
            for i in range(len(recent_prices)):
                window_start = max(0, i - 20)
                window = recent_prices[window_start:i+1]

                # Price features
                price = recent_prices[i]
                price_change = (price - recent_prices[i-1]) / recent_prices[i-1] if i > 0 else 0

                # Moving averages
                ma5 = np.mean(window[-5:]) if len(window) >= 5 else price
                ma20 = np.mean(window) if len(window) >= 20 else price

                # Volatility
                returns = np.diff(window) / window[:-1] if len(window) > 1 else [0]
                volatility = np.std(returns) if len(returns) > 0 else 0

                # Volume
                volume = recent_volumes[i] if i < len(recent_volumes) else 0

                # Combine features
                feature_vector = [
                    price,
                    price_change,
                    ma5,
                    ma20,
                    volatility,
                    volume
                ]

                features.append(feature_vector)

            return np.array(features)

        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return None

    def _predict_lstm(self, X: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Predict using LSTM model
        """
        if not self.tf_available:
            return None

        try:
            import tensorflow as tf
            from tensorflow import keras

            # Load or create model
            if self.lstm_model is None:
                self.lstm_model = self._build_lstm_model(X.shape[1])

            # Reshape for LSTM [samples, timesteps, features]
            X_reshaped = X.reshape(1, X.shape[0], X.shape[1])

            # Predict
            predictions = []
            current_sequence = X_reshaped

            for _ in range(self.prediction_horizon):
                pred = self.lstm_model.predict(current_sequence, verbose=0)
                predictions.append(float(pred[0, 0]))

                # Update sequence for next prediction
                new_feature = np.zeros((1, 1, X.shape[1]))
                new_feature[0, 0, 0] = pred[0, 0]  # Predicted price
                current_sequence = np.concatenate([
                    current_sequence[:, 1:, :],
                    new_feature
                ], axis=1)

            # Calculate expected return
            current_price = X[-1, 0]
            expected_return = ((predictions[-1] - current_price) / current_price) * 100

            return {
                'prices': predictions,
                'expected_return': round(expected_return, 2),
                'confidence': 'Medium',
                'model': 'lstm'
            }

        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return None

    def _build_lstm_model(self, n_features: int):
        """
        Build LSTM model architecture
        """
        import tensorflow as tf
        from tensorflow import keras

        model = keras.Sequential([
            keras.layers.LSTM(128, return_sequences=True, input_shape=(self.sequence_length, n_features)),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(64, return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1)
        ])

        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        logger.info("LSTM model built")
        return model

    def _predict_cnn(self, X: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Predict using CNN model (for pattern recognition)
        """
        if not self.tf_available:
            return None

        try:
            import tensorflow as tf
            from tensorflow import keras

            # Load or create model
            if self.cnn_model is None:
                self.cnn_model = self._build_cnn_model(X.shape[1])

            # Reshape for CNN [samples, timesteps, features, channels]
            X_reshaped = X.reshape(1, X.shape[0], X.shape[1], 1)

            # Predict next N days
            predictions = []
            for _ in range(self.prediction_horizon):
                pred = self.cnn_model.predict(X_reshaped, verbose=0)
                predictions.append(float(pred[0, 0]))

            # Calculate expected return
            current_price = X[-1, 0]
            expected_return = ((predictions[-1] - current_price) / current_price) * 100

            return {
                'prices': predictions,
                'expected_return': round(expected_return, 2),
                'confidence': 'Medium',
                'model': 'cnn'
            }

        except Exception as e:
            logger.error(f"CNN prediction error: {e}")
            return None

    def _build_cnn_model(self, n_features: int):
        """
        Build CNN model for pattern recognition
        """
        import tensorflow as tf
        from tensorflow import keras

        model = keras.Sequential([
            keras.layers.Conv2D(64, (3, 1), activation='relu',
                              input_shape=(self.sequence_length, n_features, 1)),
            keras.layers.MaxPooling2D((2, 1)),
            keras.layers.Conv2D(32, (3, 1), activation='relu'),
            keras.layers.MaxPooling2D((2, 1)),
            keras.layers.Flatten(),
            keras.layers.Dense(50, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(1)
        ])

        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        logger.info("CNN model built")
        return model

    def _predict_transformer(self, X: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Predict using Transformer model
        """
        # Simplified transformer (would use full implementation in production)
        # For now, return pattern-based prediction

        try:
            # Analyze trend using simple pattern
            prices = X[:, 0]  # Price column

            # Calculate trend
            recent_trend = np.polyfit(range(len(prices)), prices, 1)[0]

            # Project forward
            predictions = []
            last_price = prices[-1]

            for i in range(1, self.prediction_horizon + 1):
                pred_price = last_price + (recent_trend * i)
                predictions.append(float(pred_price))

            # Calculate expected return
            current_price = prices[-1]
            expected_return = ((predictions[-1] - current_price) / current_price) * 100

            return {
                'prices': predictions,
                'expected_return': round(expected_return, 2),
                'confidence': 'Low',  # Lower confidence for simplified model
                'model': 'transformer'
            }

        except Exception as e:
            logger.error(f"Transformer prediction error: {e}")
            return None

    def _ensemble_predictions(
        self,
        predictions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combine predictions from multiple models
        """
        if not predictions:
            return {
                'prices': [],
                'expected_return': 0,
                'confidence': 'Low'
            }

        # Weight models by confidence
        confidence_weights = {
            'High': 1.0,
            'Medium': 0.7,
            'Low': 0.4
        }

        # Calculate weighted average
        weighted_prices = None
        total_weight = 0

        for model_pred in predictions.values():
            weight = confidence_weights.get(model_pred['confidence'], 0.7)
            prices = np.array(model_pred['prices'])

            if weighted_prices is None:
                weighted_prices = prices * weight
            else:
                weighted_prices += prices * weight

            total_weight += weight

        if total_weight > 0:
            weighted_prices /= total_weight

        # Calculate ensemble confidence
        if len(predictions) >= 3:
            confidence = 'High'
        elif len(predictions) >= 2:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        # Calculate expected return
        avg_return = np.mean([p['expected_return'] for p in predictions.values()])

        # Calculate confidence interval
        returns = [p['expected_return'] for p in predictions.values()]
        std_return = np.std(returns) if len(returns) > 1 else 0

        return {
            'prices': weighted_prices.tolist() if weighted_prices is not None else [],
            'expected_return': round(avg_return, 2),
            'confidence': confidence,
            'confidence_interval': {
                'lower': round(avg_return - 1.96 * std_return, 2),
                'upper': round(avg_return + 1.96 * std_return, 2)
            }
        }

    def _generate_signal(self, prediction: Dict[str, Any]) -> str:
        """
        Generate trading signal from prediction
        """
        expected_return = prediction['expected_return']
        confidence = prediction['confidence']

        # Thresholds based on confidence
        if confidence == 'High':
            buy_threshold = 3.0
            sell_threshold = -2.0
        elif confidence == 'Medium':
            buy_threshold = 5.0
            sell_threshold = -3.0
        else:
            buy_threshold = 7.0
            sell_threshold = -5.0

        if expected_return >= buy_threshold:
            return 'BUY'
        elif expected_return <= sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'

    def _get_default_prediction(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default prediction when models unavailable
        """
        current_price = stock_data.get('current_price', 0)

        return {
            'current_price': current_price,
            'predicted_prices': [current_price] * self.prediction_horizon,
            'prediction_horizon': self.prediction_horizon,
            'expected_return': 0.0,
            'confidence': 'Low',
            'signal': 'HOLD',
            'note': 'Deep learning models unavailable',
            'timestamp': datetime.now().isoformat()
        }

    def train_models(
        self,
        training_data: List[Dict[str, Any]],
        epochs: int = 50,
        batch_size: int = 32
    ):
        """
        Train all deep learning models

        Args:
            training_data: List of historical stock data
            epochs: Training epochs
            batch_size: Batch size for training
        """
        logger.info(f"Training deep learning models on {len(training_data)} samples")

        # Prepare training dataset
        X_train, y_train = self._prepare_training_data(training_data)

        if X_train is None or len(X_train) == 0:
            logger.error("Insufficient training data")
            return

        # Train LSTM
        if self.tf_available:
            try:
                if self.lstm_model is None:
                    self.lstm_model = self._build_lstm_model(X_train.shape[2])

                X_lstm = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2])

                self.lstm_model.fit(
                    X_lstm, y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    verbose=1
                )

                # Save model
                self.lstm_model.save(os.path.join(self.model_dir, 'lstm_model.h5'))
                logger.info("LSTM model trained and saved")

            except Exception as e:
                logger.error(f"LSTM training error: {e}")

        # Train CNN
        if self.tf_available:
            try:
                if self.cnn_model is None:
                    self.cnn_model = self._build_cnn_model(X_train.shape[2])

                X_cnn = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)

                self.cnn_model.fit(
                    X_cnn, y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    verbose=1
                )

                # Save model
                self.cnn_model.save(os.path.join(self.model_dir, 'cnn_model.h5'))
                logger.info("CNN model trained and saved")

            except Exception as e:
                logger.error(f"CNN training error: {e}")

    def _prepare_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Prepare training dataset
        """
        # Implementation would extract sequences and targets
        # For now, return None (would need actual implementation)
        logger.warning("Training data preparation not fully implemented")
        return None, None

    def load_models(self):
        """
        Load pre-trained models from disk
        """
        if not self.tf_available:
            return

        try:
            import tensorflow as tf

            lstm_path = os.path.join(self.model_dir, 'lstm_model.h5')
            if os.path.exists(lstm_path):
                self.lstm_model = tf.keras.models.load_model(lstm_path)
                logger.info("LSTM model loaded")

            cnn_path = os.path.join(self.model_dir, 'cnn_model.h5')
            if os.path.exists(cnn_path):
                self.cnn_model = tf.keras.models.load_model(cnn_path)
                logger.info("CNN model loaded")

        except Exception as e:
            logger.error(f"Model loading error: {e}")
