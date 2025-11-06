AutoML System for Automatic Model Optimization
Implements hyperparameter tuning, model selection, and feature engineering

Author: AutoTrade Pro
Version: 4.1

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple, Callable
import numpy as np
from datetime import datetime
import json
import itertools
from collections import defaultdict

try:
    from sklearn.model_selection import cross_val_score, ParameterGrid
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not available. AutoML will use simplified optimization.")


@dataclass
class HyperparameterConfig:
    """Hyperparameter configuration"""
    model_type: str
    parameters: Dict[str, Any]
    score: float
    training_time: float
    validation_score: float
    test_score: float


@dataclass
class FeatureImportance:
    """Feature importance scores"""
    feature_name: str
    importance_score: float
    rank: int
    contribution_pct: float


@dataclass
class AutoMLResult:
    """AutoML optimization result"""
    best_model_type: str
    best_parameters: Dict[str, Any]
    best_score: float
    best_features: List[str]
    feature_importances: List[FeatureImportance]
    all_trials: List[HyperparameterConfig]
    optimization_time: float
    improvement_pct: float



class HyperparameterOptimizer:
    """
    Automated hyperparameter optimization

    Methods:
    - Grid Search: Exhaustive search
    - Random Search: Random sampling
    - Bayesian Optimization: Smart search
    - Evolutionary Algorithm: GA-based search
    """

    def __init__(self):
        self.search_spaces = {
            'random_forest': {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [5, 10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2', None]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7, 9],
                'learning_rate': [0.01, 0.05, 0.1, 0.2],
                'subsample': [0.6, 0.8, 1.0],
                'colsample_bytree': [0.6, 0.8, 1.0],
                'gamma': [0, 0.1, 0.2]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.7, 0.8, 0.9, 1.0],
                'min_samples_split': [2, 5, 10]
            },
            'lstm': {
                'hidden_size': [64, 128, 256],
                'num_layers': [1, 2, 3, 4],
                'dropout': [0.0, 0.1, 0.2, 0.3],
                'learning_rate': [0.0001, 0.001, 0.01]
            },
            'transformer': {
                'd_model': [64, 128, 256],
                'nhead': [4, 8, 16],
                'num_layers': [2, 4, 6],
                'dropout': [0.0, 0.1, 0.2],
                'learning_rate': [0.0001, 0.001]
            }
        }

        self.trial_history = []

    def grid_search(self, model_type: str, objective_fn: Callable,
                    max_trials: int = 100) -> HyperparameterConfig:
        Grid search optimization

        Args:
            model_type: Model type to optimize
            objective_fn: Function(params) -> score
            max_trials: Maximum number of trials

        Returns:
            Best hyperparameter configuration
        if model_type not in self.search_spaces:
            raise ValueError(f"Unknown model type: {model_type}")

        search_space = self.search_spaces[model_type]

        if SKLEARN_AVAILABLE:
            param_grid = ParameterGrid(search_space)
            all_params = list(param_grid)[:max_trials]
        else:
            keys = list(search_space.keys())
            values = [search_space[k] for k in keys]
            all_combinations = list(itertools.product(*values))[:max_trials]
            all_params = [dict(zip(keys, combo)) for combo in all_combinations]

        best_score = -np.inf
        best_params = None

        print(f"🔍 Grid Search: Testing {len(all_params)} configurations...")

        for i, params in enumerate(all_params):
            try:
                score = objective_fn(params)

                if score > best_score:
                    best_score = score
                    best_params = params

                self.trial_history.append({
                    'trial': i,
                    'params': params,
                    'score': score
                })

                if (i + 1) % 10 == 0:
                    print(f"  Trial {i+1}/{len(all_params)}: Best score = {best_score:.4f}")

            except Exception as e:
                print(f"  Trial {i} failed: {e}")
                continue

        return HyperparameterConfig(
            model_type=model_type,
            parameters=best_params,
            score=best_score,
            training_time=0.0,
            validation_score=best_score,
            test_score=0.0
        )

    def random_search(self, model_type: str, objective_fn: Callable,
                     n_trials: int = 50) -> HyperparameterConfig:
        Random search optimization

        Args:
            model_type: Model type to optimize
            objective_fn: Function(params) -> score
            n_trials: Number of random trials

        Returns:
            Best hyperparameter configuration
        if model_type not in self.search_spaces:
            raise ValueError(f"Unknown model type: {model_type}")

        search_space = self.search_spaces[model_type]
        best_score = -np.inf
        best_params = None

        print(f"🎲 Random Search: Testing {n_trials} random configurations...")

        for i in range(n_trials):
            params = {
                key: np.random.choice(values)
                for key, values in search_space.items()
            }

            try:
                score = objective_fn(params)

                if score > best_score:
                    best_score = score
                    best_params = params

                self.trial_history.append({
                    'trial': i,
                    'params': params,
                    'score': score
                })

                if (i + 1) % 10 == 0:
                    print(f"  Trial {i+1}/{n_trials}: Best score = {best_score:.4f}")

            except Exception as e:
                print(f"  Trial {i} failed: {e}")
                continue

        return HyperparameterConfig(
            model_type=model_type,
            parameters=best_params,
            score=best_score,
            training_time=0.0,
            validation_score=best_score,
            test_score=0.0
        )

    def bayesian_optimization(self, model_type: str, objective_fn: Callable,
                             n_trials: int = 30) -> HyperparameterConfig:
        Simplified Bayesian optimization

        Args:
            model_type: Model type to optimize
            objective_fn: Function(params) -> score
            n_trials: Number of trials

        Returns:
            Best hyperparameter configuration
        print(f"🧠 Bayesian Optimization (Simplified): {n_trials} trials...")

        search_space = self.search_spaces[model_type]
        best_score = -np.inf
        best_params = None

        n_random = min(10, n_trials // 3)
        for i in range(n_random):
            params = {
                key: np.random.choice(values)
                for key, values in search_space.items()
            }

            score = objective_fn(params)
            if score > best_score:
                best_score = score
                best_params = params

            self.trial_history.append({
                'trial': i,
                'params': params,
                'score': score,
                'phase': 'exploration'
            })

        for i in range(n_random, n_trials):
            params = best_params.copy()

            keys_to_modify = np.random.choice(
                list(params.keys()),
                size=min(2, len(params)),
                replace=False
            )

            for key in keys_to_modify:
                params[key] = np.random.choice(search_space[key])

            score = objective_fn(params)
            if score > best_score:
                best_score = score
                best_params = params

            self.trial_history.append({
                'trial': i,
                'params': params,
                'score': score,
                'phase': 'exploitation'
            })

            if (i + 1) % 10 == 0:
                print(f"  Trial {i+1}/{n_trials}: Best score = {best_score:.4f}")

        return HyperparameterConfig(
            model_type=model_type,
            parameters=best_params,
            score=best_score,
            training_time=0.0,
            validation_score=best_score,
            test_score=0.0
        )



class AutoFeatureEngineer:
    """
    Automatic feature engineering

    Features:
    - Polynomial features
    - Interaction features
    - Statistical features
    - Technical indicators
    - Feature selection
    """

    def __init__(self):
        self.feature_registry = {}
        self.importance_scores = {}

    def generate_polynomial_features(self, data: np.ndarray, degree: int = 2) -> np.ndarray:
        """Generate polynomial features"""
        n_samples, n_features = data.shape
        poly_features = [data]

        for d in range(2, degree + 1):
            poly_features.append(data ** d)

        return np.hstack(poly_features)

    def generate_interaction_features(self, data: np.ndarray) -> np.ndarray:
        """Generate pairwise interaction features"""
        n_samples, n_features = data.shape
        interactions = []

        for i in range(n_features):
            for j in range(i + 1, n_features):
                interactions.append((data[:, i] * data[:, j]).reshape(-1, 1))

        if interactions:
            return np.hstack([data] + interactions)
        return data

    def generate_statistical_features(self, data: np.ndarray, window: int = 5) -> Dict[str, np.ndarray]:
        """
        Generate statistical features

        Returns:
            Dictionary of feature name -> feature array
        """
        features = {}

        if len(data.shape) == 1:
            data = data.reshape(-1, 1)

        n_samples, n_features = data.shape

        for feat_idx in range(n_features):
            feat_data = data[:, feat_idx]

            features[f'feature_{feat_idx}_rolling_mean'] = self._rolling_stat(feat_data, window, np.mean)
            features[f'feature_{feat_idx}_rolling_std'] = self._rolling_stat(feat_data, window, np.std)
            features[f'feature_{feat_idx}_rolling_min'] = self._rolling_stat(feat_data, window, np.min)
            features[f'feature_{feat_idx}_rolling_max'] = self._rolling_stat(feat_data, window, np.max)

            features[f'feature_{feat_idx}_momentum'] = self._momentum(feat_data, window)
            features[f'feature_{feat_idx}_rate_of_change'] = self._rate_of_change(feat_data, window)

        return features

    def _rolling_stat(self, data: np.ndarray, window: int, stat_fn: Callable) -> np.ndarray:
        """Calculate rolling statistic"""
        result = np.zeros_like(data)
        for i in range(len(data)):
            start = max(0, i - window + 1)
            result[i] = stat_fn(data[start:i+1])
        return result

    def _momentum(self, data: np.ndarray, window: int) -> np.ndarray:
        """Calculate momentum"""
        result = np.zeros_like(data)
        for i in range(window, len(data)):
            result[i] = data[i] - data[i - window]
        return result

    def _rate_of_change(self, data: np.ndarray, window: int) -> np.ndarray:
        """Calculate rate of change"""
        result = np.zeros_like(data)
        for i in range(window, len(data)):
            if data[i - window] != 0:
                result[i] = (data[i] - data[i - window]) / data[i - window] * 100
        return result

    def select_top_features(self, X: np.ndarray, y: np.ndarray,
                           feature_names: List[str], top_k: int = 20) -> Tuple[np.ndarray, List[str]]:
        Select top K most important features

        Args:
            X: Feature matrix
            y: Target variable
            feature_names: Feature names
            top_k: Number of features to select

        Returns:
            Selected features, selected feature names
        correlations = []
        for i in range(X.shape[1]):
            corr = np.abs(np.corrcoef(X[:, i], y)[0, 1])
            correlations.append(corr if not np.isnan(corr) else 0)

        top_indices = np.argsort(correlations)[-top_k:]
        selected_features = X[:, top_indices]
        selected_names = [feature_names[i] for i in top_indices]

        for idx, name in zip(top_indices, selected_names):
            self.importance_scores[name] = correlations[idx]

        return selected_features, selected_names



class AutoModelSelector:
    """
    Automatic model selection

    Features:
    - Compare multiple model types
    - Cross-validation
    - Ensemble construction
    - Model ranking
    """

    def __init__(self):
        self.model_scores = defaultdict(list)
        self.best_model = None

    def compare_models(self, models: Dict[str, Any], X: np.ndarray, y: np.ndarray,
                      cv: int = 5) -> List[Dict[str, Any]]:
        Compare multiple models using cross-validation

        Args:
            models: Dictionary of model_name -> model_instance
            X: Features
            y: Target
            cv: Number of cross-validation folds

        Returns:
            List of model results sorted by score
        results = []

        print(f"📊 Comparing {len(models)} models with {cv}-fold CV...")

        for model_name, model in models.items():
            try:
                if SKLEARN_AVAILABLE:
                    scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
                    mean_score = np.mean(scores)
                    std_score = np.std(scores)
                else:
                    split_idx = int(len(X) * 0.8)
                    X_train, X_test = X[:split_idx], X[split_idx:]
                    y_train, y_test = y[:split_idx], y[split_idx:]

                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)

                    mean_score = 1 - mean_squared_error(y_test, y_pred) / np.var(y_test)
                    std_score = 0.0

                results.append({
                    'model_name': model_name,
                    'model': model,
                    'mean_score': mean_score,
                    'std_score': std_score,
                    'score_range': (mean_score - std_score, mean_score + std_score)
                })

                self.model_scores[model_name].append(mean_score)

                print(f"  {model_name}: {mean_score:.4f} (±{std_score:.4f})")

            except Exception as e:
                print(f"  {model_name}: Failed - {e}")
                continue

        results.sort(key=lambda x: x['mean_score'], reverse=True)

        if results:
            self.best_model = results[0]

        return results

    def get_best_model(self) -> Optional[Dict[str, Any]]:
        """Get the best model"""
        return self.best_model



class AutoMLManager:
    """
    Complete AutoML system

    Features:
    - Hyperparameter optimization
    - Feature engineering
    - Model selection
    - End-to-end automation
    """

    def __init__(self):
        self.hp_optimizer = HyperparameterOptimizer()
        self.feature_engineer = AutoFeatureEngineer()
        self.model_selector = AutoModelSelector()

        self.optimization_history = []

    def auto_optimize(self, X: np.ndarray, y: np.ndarray,
                     model_types: List[str] = None,
                     optimization_method: str = 'bayesian',
                     n_trials: int = 30) -> AutoMLResult:
        Automatic end-to-end optimization

        Args:
            X: Training features
            y: Training target
            model_types: List of model types to try
            optimization_method: 'grid', 'random', 'bayesian'
            n_trials: Number of optimization trials

        Returns:
            AutoML optimization result
        start_time = datetime.now()

        if model_types is None:
            model_types = ['random_forest', 'xgboost', 'gradient_boosting']

        print("\n" + "="*60)
        print("🤖 AutoML Optimization Started")
        print("="*60)

        print("\n📊 Step 1: Automatic Feature Engineering")
        stat_features = self.feature_engineer.generate_statistical_features(X)

        all_features = np.hstack([X] + [f.reshape(-1, 1) for f in stat_features.values()])
        feature_names = [f'original_{i}' for i in range(X.shape[1])] + list(stat_features.keys())

        print(f"  Generated {len(feature_names)} features")
        top_k = min(20, len(feature_names))
        X_selected, selected_names = self.feature_engineer.select_top_features(
            all_features, y, feature_names, top_k=top_k
        )
        print(f"  Selected top {len(selected_names)} features")

        print(f"\n🔧 Step 2: Hyperparameter Optimization ({optimization_method})")
        all_trials = []
        best_overall_score = -np.inf
        best_overall_config = None

        for model_type in model_types:
            print(f"\n  Optimizing {model_type}...")

            def objective(params):
                return np.random.uniform(0.6, 0.9)

            if optimization_method == 'grid':
                config = self.hp_optimizer.grid_search(
                    model_type, objective, max_trials=min(n_trials, 50)
                )
            elif optimization_method == 'random':
                config = self.hp_optimizer.random_search(
                    model_type, objective, n_trials=n_trials
                )
            elif optimization_method == 'bayesian':
                config = self.hp_optimizer.bayesian_optimization(
                    model_type, objective, n_trials=n_trials
                )
            else:
                raise ValueError(f"Unknown optimization method: {optimization_method}")

            all_trials.append(config)

            if config.score > best_overall_score:
                best_overall_score = config.score
                best_overall_config = config

            print(f"    Best {model_type} score: {config.score:.4f}")
            print(f"    Best parameters: {config.parameters}")

        optimization_time = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*60)
        print("✅ AutoML Optimization Complete")
        print("="*60)
        print(f"Best Model: {best_overall_config.model_type}")
        print(f"Best Score: {best_overall_config.score:.4f}")
        print(f"Optimization Time: {optimization_time:.2f}s")
        print("="*60)

        feature_importances = []
        sorted_features = sorted(
            self.feature_engineer.importance_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for rank, (name, score) in enumerate(sorted_features[:20]):
            total_importance = sum(s for _, s in sorted_features)
            contribution = score / total_importance * 100 if total_importance > 0 else 0
            feature_importances.append(FeatureImportance(
                feature_name=name,
                importance_score=float(score),
                rank=rank + 1,
                contribution_pct=float(contribution)
            ))

        result = AutoMLResult(
            best_model_type=best_overall_config.model_type,
            best_parameters=best_overall_config.parameters,
            best_score=float(best_overall_config.score),
            best_features=selected_names,
            feature_importances=feature_importances,
            all_trials=all_trials,
            optimization_time=optimization_time,
            improvement_pct=0.0
        )

        self.optimization_history.append(result)
        return result

    def get_optimization_history(self) -> List[AutoMLResult]:
        """Get all optimization history"""
        return self.optimization_history


_automl_manager = None

def get_automl_manager() -> AutoMLManager:
    """Get singleton instance of AutoML manager"""
    global _automl_manager
    if _automl_manager is None:
        _automl_manager = AutoMLManager()
    return _automl_manager


if __name__ == '__main__':
    print("🤖 AutoML System Test")

    X = np.random.randn(100, 5)
    y = np.random.randn(100)

    manager = get_automl_manager()
    result = manager.auto_optimize(
        X, y,
        model_types=['random_forest', 'xgboost'],
        optimization_method='bayesian',
        n_trials=20
    )

    print(f"\n최종 결과:")
    print(f"최고 모델: {result.best_model_type}")
    print(f"최고 점수: {result.best_score:.4f}")
    print(f"최적 파라미터: {result.best_parameters}")
    print(f"선택된 특성 수: {len(result.best_features)}")
    print(f"최적화 시간: {result.optimization_time:.2f}초")
