virtual_trading/trade_logger.py
거래 로그 및 분석
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import json


class TradeLogger:
    """거래 로거 - 모든 가상 거래 기록 및 분석"""

    def __init__(self, log_dir: str = "data/virtual_trading/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.trades: List[Dict] = []

    def log_trade(self, trade_data: Dict):
        """거래 로그 기록"""
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            **trade_data
        }
        self.trades.append(trade_record)

        today = datetime.now().strftime('%Y%m%d')
        log_file = self.log_dir / f"trades_{today}.jsonl"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trade_record, ensure_ascii=False) + '\n')

    def log_buy(self, strategy: str, stock_code: str, stock_name: str,
                price: int, quantity: int, reason: str = ""):
        self.log_trade({
            'type': 'BUY',
            'strategy': strategy,
            'stock_code': stock_code,
            'stock_name': stock_name,
            'price': price,
            'quantity': quantity,
            'amount': price * quantity,
            'reason': reason,
        })

    def log_sell(self, strategy: str, stock_code: str, stock_name: str,
                 price: int, quantity: int, realized_pnl: int,
                 pnl_rate: float, reason: str = ""):
        self.log_trade({
            'type': 'SELL',
            'strategy': strategy,
            'stock_code': stock_code,
            'stock_name': stock_name,
            'price': price,
            'quantity': quantity,
            'amount': price * quantity,
            'realized_pnl': realized_pnl,
            'pnl_rate': pnl_rate,
            'reason': reason,
        })

    def get_trade_analysis(self, strategy: str = None) -> Dict:
        """거래 분석"""
        if not self.trades:
            return {}

        trades = self.trades
        if strategy:
            trades = [t for t in trades if t.get('strategy') == strategy]

        if not trades:
            return {}

        sell_trades = [t for t in trades if t['type'] == 'SELL']

        if not sell_trades:
            return {
                'total_trades': len([t for t in trades if t['type'] == 'BUY']),
                'total_buys': len([t for t in trades if t['type'] == 'BUY']),
                'total_sells': 0,
                'win_trades': 0,
                'lose_trades': 0,
            }

        win_trades = [t for t in sell_trades if t['realized_pnl'] > 0]
        lose_trades = [t for t in sell_trades if t['realized_pnl'] <= 0]

        total_profit = sum(t['realized_pnl'] for t in win_trades)
        total_loss = sum(t['realized_pnl'] for t in lose_trades)

        avg_profit = total_profit / len(win_trades) if win_trades else 0
        avg_loss = total_loss / len(lose_trades) if lose_trades else 0

        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else 0

        best_trade = max(sell_trades, key=lambda x: x['realized_pnl']) if sell_trades else None
        worst_trade = min(sell_trades, key=lambda x: x['realized_pnl']) if sell_trades else None

        return {
            'total_trades': len(sell_trades),
            'total_buys': len([t for t in trades if t['type'] == 'BUY']),
            'total_sells': len(sell_trades),
            'win_trades': len(win_trades),
            'lose_trades': len(lose_trades),
            'win_rate': len(win_trades) / len(sell_trades) if sell_trades else 0,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'best_trade': {
                'stock': f"{best_trade['stock_name']}({best_trade['stock_code']})",
                'pnl': best_trade['realized_pnl'],
                'pnl_rate': best_trade['pnl_rate'],
            } if best_trade else None,
            'worst_trade': {
                'stock': f"{worst_trade['stock_name']}({worst_trade['stock_code']})",
                'pnl': worst_trade['realized_pnl'],
                'pnl_rate': worst_trade['pnl_rate'],
            } if worst_trade else None,
        }

    def get_strategy_comparison(self) -> Dict[str, Dict]:
        """전략별 비교"""
        strategies = set(t['strategy'] for t in self.trades if 'strategy' in t)
        return {
            strategy: self.get_trade_analysis(strategy)
            for strategy in strategies
        }

    def get_stock_analysis(self, stock_code: str) -> Dict:
        """종목별 거래 분석"""
        stock_trades = [t for t in self.trades if t.get('stock_code') == stock_code]

        if not stock_trades:
            return {}

        buy_trades = [t for t in stock_trades if t['type'] == 'BUY']
        sell_trades = [t for t in stock_trades if t['type'] == 'SELL']

        total_buy_amount = sum(t['amount'] for t in buy_trades)
        total_sell_amount = sum(t['amount'] for t in sell_trades)
        total_realized_pnl = sum(t['realized_pnl'] for t in sell_trades)

        return {
            'stock_code': stock_code,
            'stock_name': stock_trades[0].get('stock_name', ''),
            'total_buys': len(buy_trades),
            'total_sells': len(sell_trades),
            'total_buy_amount': total_buy_amount,
            'total_sell_amount': total_sell_amount,
            'total_realized_pnl': total_realized_pnl,
            'strategies': list(set(t['strategy'] for t in stock_trades if 'strategy' in t)),
        }

    def get_recent_trades(self, limit: int = 10, strategy: str = None) -> List[Dict]:
        """최근 거래 내역"""
        trades = self.trades
        if strategy:
            trades = [t for t in trades if t.get('strategy') == strategy]

        return sorted(trades, key=lambda x: x['timestamp'], reverse=True)[:limit]

    def print_summary(self):
        """거래 요약 출력"""
        analysis = self.get_trade_analysis()

        if not analysis:
            print("📊 거래 내역 없음")
            return

        print("\n" + "="*60)
        print("📊 가상 거래 로그 요약")
        print("="*60)

        print(f"\n총 거래: {analysis['total_buys']}회 매수, {analysis['total_sells']}회 매도")

        if analysis['total_sells'] > 0:
            print(f"승률: {analysis['win_rate']:.1%} ({analysis['win_trades']}승 {analysis['lose_trades']}패)")
            print(f"총 수익: {analysis['total_profit']:+,}원")
            print(f"총 손실: {analysis['total_loss']:+,}원")
            print(f"평균 수익: {analysis['avg_profit']:+,.0f}원")
            print(f"평균 손실: {analysis['avg_loss']:+,.0f}원")
            print(f"Profit Factor: {analysis['profit_factor']:.2f}")

            if analysis['best_trade']:
                print(f"\n최고 거래: {analysis['best_trade']['stock']} "
                      f"{analysis['best_trade']['pnl']:+,}원 ({analysis['best_trade']['pnl_rate']:+.1%})")

            if analysis['worst_trade']:
                print(f"최악 거래: {analysis['worst_trade']['stock']} "
                      f"{analysis['worst_trade']['pnl']:+,}원 ({analysis['worst_trade']['pnl_rate']:+.1%})")

        print("="*60)

    def load_historical_trades(self, days: int = 7):
        """과거 로그 파일 불러오기"""
        from datetime import timedelta

        today = datetime.now()
        loaded_count = 0

        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y%m%d')
            log_file = self.log_dir / f"trades_{date}.jsonl"

            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            trade = json.loads(line.strip())
                            self.trades.append(trade)
                            loaded_count += 1
                        except json.JSONDecodeError:
                            continue

        return loaded_count


__all__ = ['TradeLogger']
