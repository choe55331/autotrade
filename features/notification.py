Notification System
Multi-channel notification system for trading alerts

Features:
- Sound notifications
- Desktop notifications
- Telegram bot integration
- Priority-based alerting
- Notification history
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class NotificationChannel(Enum):
    """Notification channels"""
    SOUND = 'sound'
    DESKTOP = 'desktop'
    TELEGRAM = 'telegram'
    EMAIL = 'email'


@dataclass
class Notification:
    """Single notification"""
    id: str
    timestamp: str
    priority: str
    category: str
    title: str
    message: str
    channels: List[str]
    data: Dict[str, Any] = None
    delivered: bool = False
    read: bool = False


class NotificationManager:
    """
    Multi-channel notification manager

    Handles sound, desktop, and telegram notifications
    """

    def __init__(self):
        """Initialize notification manager"""
        self.enabled = True
        self.sound_enabled = True
        self.desktop_enabled = True
        self.telegram_enabled = False

        try:
            from config import get_credentials
            creds = get_credentials()
            telegram_config = creds.get_telegram_config()
            self.telegram_bot_token: Optional[str] = telegram_config.get('bot_token')
            self.telegram_chat_id: Optional[str] = telegram_config.get('chat_id')

            if self.telegram_bot_token and self.telegram_chat_id:
                self.telegram_enabled = True
                logger.info("Telegram 설정을 credentials에서 로드했습니다")
        except Exception as e:
            logger.warning(f"Telegram credentials 로드 실패: {e}")
            self.telegram_bot_token: Optional[str] = None
            self.telegram_chat_id: Optional[str] = None

        self.notifications: List[Notification] = []

        self.sounds_dir = Path('dashboard/static/sounds')
        self.sounds_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = Path('config/notifications.json')
        self.history_file = Path('data/notifications.json')

        self._load_config()
        self._load_history()

    def _load_config(self):
        """Load notification config"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.enabled = config.get('enabled', True)
                    self.sound_enabled = config.get('sound_enabled', True)
                    self.desktop_enabled = config.get('desktop_enabled', True)
                    self.telegram_enabled = config.get('telegram_enabled', False)
                    self.telegram_bot_token = config.get('telegram_bot_token')
                    self.telegram_chat_id = config.get('telegram_chat_id')
        except Exception as e:
            logger.error(f"Error loading notification config: {e}")

    def _save_config(self):
        """Save notification config"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'enabled': self.enabled,
                    'sound_enabled': self.sound_enabled,
                    'desktop_enabled': self.desktop_enabled,
                    'telegram_enabled': self.telegram_enabled,
                    'telegram_bot_token': self.telegram_bot_token,
                    'telegram_chat_id': self.telegram_chat_id
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving notification config: {e}")

    def _load_history(self):
        """Load notification history"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notifications = [Notification(**n) for n in data.get('notifications', [])][-100:]
        except Exception as e:
            logger.error(f"Error loading notification history: {e}")

    def _save_history(self):
        """Save notification history"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'notifications': [asdict(n) for n in self.notifications[-100:]],
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving notification history: {e}")

    def send(
        self,
        title: str,
        message: str,
        priority: str = 'medium',
        category: str = 'system',
        channels: List[str] = None,
        data: Dict[str, Any] = None
    ) -> Notification:
        Send notification

        Args:
            title: Notification title
            message: Notification message
            priority: Priority level (low/medium/high/critical)
            category: Category (trade/ai/alert/system)
            channels: List of channels to use (None = auto-select based on priority)
            data: Additional data

        Returns:
            Notification object
        if not self.enabled:
            return None

        if channels is None:
            channels = self._auto_select_channels(priority)

        notification = Notification(
            id=f"notif_{int(datetime.now().timestamp())}",
            timestamp=datetime.now().isoformat(),
            priority=priority,
            category=category,
            title=title,
            message=message,
            channels=channels,
            data=data,
            delivered=False,
            read=False
        )

        for channel in channels:
            try:
                if channel == 'sound' and self.sound_enabled:
                    self._send_sound(notification)
                elif channel == 'desktop' and self.desktop_enabled:
                    self._send_desktop(notification)
                elif channel == 'telegram' and self.telegram_enabled:
                    self._send_telegram(notification)
            except Exception as e:
                logger.error(f"Error sending notification to {channel}: {e}")

        notification.delivered = True
        self.notifications.append(notification)
        self._save_history()

        logger.info(f"Notification sent: [{priority}] {title}")

        return notification

    def _auto_select_channels(self, priority: str) -> List[str]:
        """Auto-select channels based on priority"""
        if priority == 'critical':
            return ['sound', 'desktop', 'telegram']
        elif priority == 'high':
            return ['sound', 'desktop']
        elif priority == 'medium':
            return ['desktop']
        else:
            return []

    def _send_sound(self, notification: Notification):
        """Play sound notification"""
        try:
            sound_map = {
                'critical': 'critical_alert.wav',
                'high': 'high_alert.wav',
                'medium': 'notification.wav',
                'low': 'soft_ping.wav'
            }

            sound_file = sound_map.get(notification.priority, 'notification.wav')
            sound_path = self.sounds_dir / sound_file

            if not sound_path.exists():
                logger.info(f"Would play sound: {sound_file}")
                return


            logger.info(f"🔊 Sound played: {sound_file}")

        except Exception as e:
            logger.error(f"Error playing sound: {e}")

    def _send_desktop(self, notification: Notification):
        """Send desktop notification"""
        try:

            try:
                from plyer import notification as plyer_notif
                plyer_notif.notify(
                    title=notification.title,
                    message=notification.message,
                    app_name='AutoTrade Pro',
                    timeout=10
                )
                logger.info(f"📢 Desktop notification sent: {notification.title}")
            except ImportError:
                logger.info(f"📢 [Desktop] {notification.title}: {notification.message}")

        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")

    def _send_telegram(self, notification: Notification):
        """Send Telegram notification"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured")
            return

        try:
            import requests

            priority_emoji = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': 'ℹ️',
                'low': '💬'
            }

            emoji = priority_emoji.get(notification.priority, 'ℹ️')

            telegram_message = f"{emoji} **{notification.title}**\n\n{notification.message}"

            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': telegram_message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, json=payload, timeout=5)

            if response.status_code == 200:
                logger.info(f"📱 Telegram notification sent: {notification.title}")
            else:
                logger.error(f"Telegram API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")


    def notify_trade(
        self,
        action: str,
        stock_name: str,
        quantity: int,
        price: float,
        reason: str
    ):
        title = f"{'🟢 매수' if action == 'buy' else '🔴 매도'}: {stock_name}"
        message = f"""
수량: {quantity}주
가격: {price:,}원
총액: {price * quantity:,}원
이유: {reason}

        self.send(
            title=title,
            message=message,
            priority='high',
            category='trade',
            data={
                'action': action,
                'stock_name': stock_name,
                'quantity': quantity,
                'price': price
            }
        )

    def notify_ai_decision(
        self,
        decision_type: str,
        stock_name: str,
        confidence: float,
        reasoning: List[str]
    ):
        title = f"🤖 AI 결정: {decision_type.upper()} - {stock_name}"
        message = f"""
신뢰도: {confidence:.0%}
이유:
{chr(10).join(f"  • {r}" for r in reasoning)}

        priority = 'high' if confidence > 0.8 else 'medium'

        self.send(
            title=title,
            message=message,
            priority=priority,
            category='ai',
            data={
                'decision_type': decision_type,
                'stock_name': stock_name,
                'confidence': confidence
            }
        )

    def notify_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        priority: str = 'medium'
    ):
        self.send(
            title=f"⚠️ {title}",
            message=message,
            priority=priority,
            category='alert'
        )

    def notify_paper_trading_result(
        self,
        strategy_name: str,
        action: str,
        stock_name: str,
        profit_pct: float
    ):
        emoji = '📈' if profit_pct > 0 else '📉'
        title = f"{emoji} 가상매매: {strategy_name}"
        message = f"""
{action}: {stock_name}
수익률: {profit_pct:+.1f}%

        self.send(
            title=title,
            message=message,
            priority='low',
            category='paper_trading'
        )

    def configure_telegram(self, bot_token: str, chat_id: str):
        """Configure Telegram integration"""
        self.telegram_bot_token = bot_token
        self.telegram_chat_id = chat_id
        self.telegram_enabled = True
        self._save_config()
        logger.info("Telegram configured")

    def get_unread_count(self) -> int:
        """Get number of unread notifications"""
        return sum(1 for n in self.notifications if not n.read)

    def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                self._save_history()
                break

    def mark_all_as_read(self):
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification.read = False
        self._save_history()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard"""
        return {
            'success': True,
            'enabled': self.enabled,
            'channels': {
                'sound': self.sound_enabled,
                'desktop': self.desktop_enabled,
                'telegram': self.telegram_enabled
            },
            'unread_count': self.get_unread_count(),
            'recent_notifications': [asdict(n) for n in self.notifications[-20:]],
            'last_updated': datetime.now().isoformat()
        }


_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get or create notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


if __name__ == '__main__':
    manager = NotificationManager()

    print("\n📢 Notification System Test")
    print("=" * 60)

    manager.notify_trade(
        action='buy',
        stock_name='삼성전자',
        quantity=100,
        price=73500,
        reason='AI 신뢰도 85%로 강력 매수'
    )

    manager.notify_ai_decision(
        decision_type='buy',
        stock_name='SK하이닉스',
        confidence=0.78,
        reasoning=[
            '거래량 1.8배 폭증',
            'RSI 45로 적정 수준',
            '돌파 변동성 전략 신호'
        ]
    )

    manager.notify_alert(
        alert_type='system',
        title='AI 모드 활성화',
        message='AI 자율 트레이딩 모드가 활성화되었습니다.',
        priority='high'
    )

    print(f"\n총 알림: {len(manager.notifications)}개")
    print(f"읽지 않은 알림: {manager.get_unread_count()}개")
