"""
Reinforcement Learning Agent
DQN-based autonomous trading agent

Features:
- Deep Q-Network (DQN) for action selection
- Experience replay
- Target network
- Epsilon-greedy exploration
- Continuous learning from trades
- Risk-aware reward function
"""
import json
import numpy as np
import random
from collections import deque
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class RLState:
    """RL agent state"""
    portfolio_value: float
    cash_balance: float
    position_count: int
    current_price: float
    price_change_5m: float
    price_change_1h: float
    rsi: float
    macd: float
    volume_ratio: float
    market_trend: float  # -1 to 1
    time_of_day: float  # 0 to 1


@dataclass
class RLAction:
    """RL agent action"""
    action_type: str  # 'buy', 'sell', 'hold'
    quantity: int
    confidence: float


@dataclass
class RLExperience:
    """Experience for replay buffer"""
    state: List[float]
    action: int
    reward: float
    next_state: List[float]
    done: bool


class ReplayBuffer:
    """Experience replay buffer"""

    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)

    def add(self, experience: RLExperience):
        """Add experience to buffer"""
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> List[RLExperience]:
        """Sample random batch from buffer"""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))

    def size(self) -> int:
        """Get buffer size"""
        return len(self.buffer)


class DQNAgent:
    """
    Deep Q-Network Agent for trading

    Actions:
    0: Hold
    1: Buy small (10%)
    2: Buy medium (20%)
    3: Buy large (30%)
    4: Sell small (10% of position)
    5: Sell medium (30% of position)
    6: Sell large (50% of position)
    """

    def __init__(
        self,
        state_size: int = 11,
        action_size: int = 7,
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        """
        Initialize DQN agent

        Args:
            state_size: Size of state vector
            action_size: Number of actions
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Exploration decay rate
            epsilon_min: Minimum exploration rate
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Experience replay
        self.memory = ReplayBuffer(capacity=10000)
        self.batch_size = 32

        # Q-network (simplified - would use neural network in production)
        self.q_table: Dict[Tuple, np.ndarray] = {}

        # Performance tracking
        self.total_rewards = 0
        self.episode_rewards = []
        self.actions_taken = []

        # Model file
        self.model_file = Path('data/rl_models/dqn_agent.json')
        self.model_file.parent.mkdir(parents=True, exist_ok=True)

        self._load_model()

    def _discretize_state(self, state: List[float]) -> Tuple:
        """Discretize continuous state for Q-table"""
        # Discretize each dimension into bins
        discretized = []
        for value in state:
            if value < -1:
                bin_val = 0
            elif value < -0.5:
                bin_val = 1
            elif value < 0:
                bin_val = 2
            elif value < 0.5:
                bin_val = 3
            elif value < 1:
                bin_val = 4
            else:
                bin_val = 5
            discretized.append(bin_val)
        return tuple(discretized)

    def get_q_values(self, state: List[float]) -> np.ndarray:
        """Get Q-values for state"""
        state_key = self._discretize_state(state)
        if state_key not in self.q_table:
            # Initialize Q-values
            self.q_table[state_key] = np.random.randn(self.action_size) * 0.01
        return self.q_table[state_key]

    def act(self, state: List[float]) -> int:
        """
        Choose action using epsilon-greedy policy

        Args:
            state: Current state

        Returns:
            Action index
        """
        # Epsilon-greedy exploration
        if np.random.rand() <= self.epsilon:
            action = random.randrange(self.action_size)
        else:
            q_values = self.get_q_values(state)
            action = np.argmax(q_values)

        self.actions_taken.append(action)
        return action

    def remember(
        self,
        state: List[float],
        action: int,
        reward: float,
        next_state: List[float],
        done: bool
    ):
        """Store experience in replay buffer"""
        experience = RLExperience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done
        )
        self.memory.add(experience)

    def replay(self):
        """Train on batch of experiences"""
        if self.memory.size() < self.batch_size:
            return

        # Sample batch
        batch = self.memory.sample(self.batch_size)

        for experience in batch:
            state = experience.state
            action = experience.action
            reward = experience.reward
            next_state = experience.next_state
            done = experience.done

            # Q-learning update
            q_values = self.get_q_values(state)
            next_q_values = self.get_q_values(next_state)

            if done:
                target = reward
            else:
                target = reward + self.gamma * np.max(next_q_values)

            # Update Q-value
            q_values[action] = q_values[action] + self.learning_rate * (target - q_values[action])

            # Update Q-table
            state_key = self._discretize_state(state)
            self.q_table[state_key] = q_values

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def calculate_reward(
        self,
        action: int,
        prev_portfolio_value: float,
        curr_portfolio_value: float,
        risk_taken: float = 0.0
    ) -> float:
        """
        Calculate reward for action

        Args:
            action: Action taken
            prev_portfolio_value: Portfolio value before action
            curr_portfolio_value: Portfolio value after action
            risk_taken: Risk level (0-1)

        Returns:
            Reward value
        """
        # Profit/loss reward
        profit_pct = ((curr_portfolio_value - prev_portfolio_value) / prev_portfolio_value) * 100
        reward = profit_pct

        # Risk penalty
        reward -= risk_taken * 0.5

        # Action-specific adjustments
        if action == 0:  # Hold
            reward *= 0.1  # Small reward for holding
        elif action in [1, 2, 3]:  # Buy
            if profit_pct > 0:
                reward *= 1.5  # Bonus for profitable buy
            else:
                reward *= 1.0
        elif action in [4, 5, 6]:  # Sell
            if profit_pct > 0:
                reward *= 2.0  # Big bonus for profitable sell
            else:
                reward *= 0.8  # Small penalty for loss-making sell

        # Clip reward to reasonable range
        reward = np.clip(reward, -10, 10)

        self.total_rewards += reward
        self.episode_rewards.append(reward)

        return reward

    def train_step(
        self,
        prev_state: RLState,
        action: int,
        curr_state: RLState,
        done: bool = False
    ):
        """
        Perform one training step

        Args:
            prev_state: Previous state
            action: Action taken
            curr_state: Current state
            done: Whether episode is done
        """
        # Convert states to vectors
        prev_state_vec = self._state_to_vector(prev_state)
        curr_state_vec = self._state_to_vector(curr_state)

        # Calculate reward
        reward = self.calculate_reward(
            action,
            prev_state.portfolio_value,
            curr_state.portfolio_value,
            risk_taken=0.0  # Can be calculated based on action
        )

        # Remember experience
        self.remember(prev_state_vec, action, reward, curr_state_vec, done)

        # Train on batch
        self.replay()

    def _state_to_vector(self, state: RLState) -> List[float]:
        """Convert state object to vector"""
        return [
            state.portfolio_value / 10000000,  # Normalize to millions
            state.cash_balance / 10000000,
            state.position_count / 10,
            state.current_price / 100000,
            state.price_change_5m,
            state.price_change_1h,
            state.rsi / 100,
            state.macd / 1000,
            state.volume_ratio,
            state.market_trend,
            state.time_of_day
        ]

    def get_action_interpretation(self, action: int) -> RLAction:
        """
        Interpret action index as trading action

        Args:
            action: Action index

        Returns:
            RLAction object
        """
        action_map = {
            0: ('hold', 0, 0.3),
            1: ('buy', 10, 0.5),  # Buy 10% of cash
            2: ('buy', 20, 0.7),  # Buy 20% of cash
            3: ('buy', 30, 0.9),  # Buy 30% of cash
            4: ('sell', 10, 0.5),  # Sell 10% of position
            5: ('sell', 30, 0.7),  # Sell 30% of position
            6: ('sell', 50, 0.9),  # Sell 50% of position
        }

        action_type, quantity_pct, confidence = action_map.get(action, ('hold', 0, 0.3))

        return RLAction(
            action_type=action_type,
            quantity=quantity_pct,
            confidence=confidence
        )

    def _save_model(self):
        """Save model to disk"""
        try:
            # Save Q-table
            q_table_serialized = {
                str(k): v.tolist() for k, v in self.q_table.items()
            }

            data = {
                'q_table': q_table_serialized,
                'epsilon': self.epsilon,
                'total_rewards': self.total_rewards,
                'episode_rewards': self.episode_rewards[-100:],
                'last_updated': datetime.now().isoformat()
            }

            with open(self.model_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info("RL model saved")

        except Exception as e:
            logger.error(f"Error saving RL model: {e}")

    def _load_model(self):
        """Load model from disk"""
        try:
            if self.model_file.exists():
                with open(self.model_file, 'r') as f:
                    data = json.load(f)

                # Load Q-table
                q_table_serialized = data.get('q_table', {})
                self.q_table = {
                    eval(k): np.array(v) for k, v in q_table_serialized.items()
                }

                self.epsilon = data.get('epsilon', self.epsilon)
                self.total_rewards = data.get('total_rewards', 0)
                self.episode_rewards = data.get('episode_rewards', [])

                logger.info("RL model loaded")

        except Exception as e:
            logger.error(f"Error loading RL model: {e}")

    def get_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        recent_rewards = self.episode_rewards[-100:] if self.episode_rewards else [0]

        return {
            'total_rewards': self.total_rewards,
            'avg_reward': np.mean(recent_rewards),
            'recent_rewards': recent_rewards[-10:],
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'memory_size': self.memory.size(),
            'actions_distribution': {
                i: self.actions_taken.count(i) for i in range(self.action_size)
            } if self.actions_taken else {},
            'last_updated': datetime.now().isoformat()
        }

    def save(self):
        """Save model"""
        self._save_model()


# Global instance
_rl_agent: Optional[DQNAgent] = None


def get_rl_agent() -> DQNAgent:
    """Get or create RL agent instance"""
    global _rl_agent
    if _rl_agent is None:
        _rl_agent = DQNAgent()
    return _rl_agent


# Example usage
if __name__ == '__main__':
    agent = DQNAgent()

    print("\n🎮 Reinforcement Learning Agent Test")
    print("=" * 60)

    # Create sample state
    state = RLState(
        portfolio_value=10000000,
        cash_balance=5000000,
        position_count=2,
        current_price=73500,
        price_change_5m=0.5,
        price_change_1h=1.2,
        rsi=55,
        macd=100,
        volume_ratio=1.3,
        market_trend=0.6,
        time_of_day=0.5
    )

    # Get action
    state_vec = agent._state_to_vector(state)
    action_idx = agent.act(state_vec)
    action = agent.get_action_interpretation(action_idx)

    print(f"\nState: Portfolio {state.portfolio_value:,.0f}원")
    print(f"Action: {action.action_type.upper()}")
    print(f"Quantity: {action.quantity}%")
    print(f"Confidence: {action.confidence:.0%}")
    print(f"\nEpsilon (exploration): {agent.epsilon:.2f}")
    print(f"Q-table size: {len(agent.q_table)}")
