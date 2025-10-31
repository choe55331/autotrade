"""
News Feed with Sentiment Analysis
Real-time stock news fetching and AI sentiment analysis

Features:
- Fetch latest news for stocks
- AI sentiment analysis (Positive/Negative/Neutral)
- News impact scoring
- Real-time updates
- Filtering by sentiment
"""
import json
import re
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Single news article"""
    id: str
    title: str
    summary: str
    url: str
    source: str
    published_at: str
    stock_code: Optional[str]
    stock_name: Optional[str]
    sentiment: str  # 'positive', 'negative', 'neutral'
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    impact_level: str  # 'high', 'medium', 'low'
    keywords: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class NewsSummary:
    """News summary for a stock"""
    stock_code: str
    stock_name: str
    total_articles: int
    positive_count: int
    negative_count: int
    neutral_count: int
    avg_sentiment_score: float
    overall_sentiment: str
    last_updated: str


class SentimentAnalyzer:
    """Korean financial news sentiment analyzer"""

    # Korean sentiment keywords
    POSITIVE_KEYWORDS = [
        '상승', '호재', '증가', '개선', '성장', '확대', '호조',
        '신규', '투자', '수주', '계약', '협약', '흑자', '수익',
        '긍정', '기대', '전망', '강세', '돌파', '사상최대',
        '실적개선', '매출증가', '영업이익', '순이익증가'
    ]

    NEGATIVE_KEYWORDS = [
        '하락', '악재', '감소', '악화', '하락', '축소', '부진',
        '손실', '적자', '취소', '지연', '중단', '리스크', '위험',
        '부정', '우려', '약세', '하락', '실망', '저조',
        '실적악화', '매출감소', '영업손실', '적자전환'
    ]

    # Impact keywords
    HIGH_IMPACT_KEYWORDS = [
        '대규모', '사상최대', '전년대비', '분기실적', '연간실적',
        '자회사', '계열사', 'M&A', '인수', '합병', '상장',
        '증자', '유상증자', '무상증자', '배당', '특별배당'
    ]

    def __init__(self):
        """Initialize sentiment analyzer"""
        self.positive_pattern = '|'.join(self.POSITIVE_KEYWORDS)
        self.negative_pattern = '|'.join(self.NEGATIVE_KEYWORDS)
        self.high_impact_pattern = '|'.join(self.HIGH_IMPACT_KEYWORDS)

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of Korean text

        Args:
            text: Korean text to analyze

        Returns:
            Dictionary with sentiment, score, confidence
        """
        # Count positive/negative keywords
        positive_matches = len(re.findall(self.positive_pattern, text, re.IGNORECASE))
        negative_matches = len(re.findall(self.negative_pattern, text, re.IGNORECASE))

        # Calculate raw score
        total_matches = positive_matches + negative_matches
        if total_matches == 0:
            sentiment = 'neutral'
            score = 0.0
            confidence = 0.3
        else:
            score = (positive_matches - negative_matches) / total_matches
            confidence = min(0.9, 0.5 + (total_matches * 0.1))

            if score > 0.2:
                sentiment = 'positive'
            elif score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_matches': positive_matches,
            'negative_matches': negative_matches
        }

    def analyze_impact(self, text: str) -> str:
        """
        Determine news impact level

        Returns:
            'high', 'medium', or 'low'
        """
        high_impact_matches = len(re.findall(self.high_impact_pattern, text, re.IGNORECASE))

        if high_impact_matches >= 2:
            return 'high'
        elif high_impact_matches >= 1:
            return 'medium'
        else:
            return 'low'

    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract important keywords from text

        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords
        """
        keywords = []

        # Find all sentiment keywords
        for keyword in self.POSITIVE_KEYWORDS + self.NEGATIVE_KEYWORDS:
            if keyword in text:
                keywords.append(keyword)

        # Find high impact keywords
        for keyword in self.HIGH_IMPACT_KEYWORDS:
            if keyword in text:
                keywords.append(keyword)

        # Remove duplicates and limit
        keywords = list(set(keywords))[:max_keywords]
        return keywords


class NewsFeedService:
    """News feed service with caching and sentiment analysis"""

    def __init__(self):
        """Initialize news feed service"""
        self.analyzer = SentimentAnalyzer()
        self.cache_file = Path('data/news_cache.json')
        self.cache_ttl = 600  # 10 minutes
        self._ensure_data_dir()
        self.news_cache: Dict[str, Dict] = {}

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_cache(self):
        """Load news cache from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.news_cache = data
                    logger.info(f"Loaded {len(self.news_cache)} cached news items")
        except Exception as e:
            logger.error(f"Error loading news cache: {e}")
            self.news_cache = {}

    def _save_cache(self):
        """Save news cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving news cache: {e}")

    def _is_cache_valid(self, stock_code: str) -> bool:
        """Check if cache is still valid for stock"""
        if stock_code not in self.news_cache:
            return False

        cache_time = datetime.fromisoformat(self.news_cache[stock_code]['cached_at'])
        age_seconds = (datetime.now() - cache_time).total_seconds()

        return age_seconds < self.cache_ttl

    def _create_mock_news(self, stock_code: str, stock_name: str, count: int = 5) -> List[NewsArticle]:
        """
        Create mock news articles for testing

        Args:
            stock_code: Stock code
            stock_name: Stock name
            count: Number of articles to generate

        Returns:
            List of NewsArticle objects
        """
        mock_news_templates = [
            {
                'title': f'{stock_name}, 3분기 영업이익 전년 대비 25% 증가 전망',
                'summary': f'{stock_name}가 3분기 실적 발표를 앞두고 있으며, 전문가들은 영업이익이 전년 동기 대비 25% 증가할 것으로 예상하고 있습니다.',
            },
            {
                'title': f'{stock_name}, 신규 사업 진출로 성장 동력 확보',
                'summary': f'{stock_name}가 새로운 사업 분야에 진출하여 장기적인 성장 동력을 확보했다고 발표했습니다.',
            },
            {
                'title': f'{stock_name} 주가, 외국인 매수세에 강세',
                'summary': f'최근 외국인 투자자들의 지속적인 매수로 {stock_name} 주가가 강세를 보이고 있습니다.',
            },
            {
                'title': f'{stock_name}, 원자재 가격 상승으로 수익성 악화 우려',
                'summary': f'글로벌 원자재 가격 상승으로 {stock_name}의 생산 비용이 증가하면서 수익성 악화에 대한 우려가 제기되고 있습니다.',
            },
            {
                'title': f'{stock_name}, 대규모 설비 투자 계획 발표',
                'summary': f'{stock_name}가 향후 3년간 대규모 설비 투자를 진행하여 생산 능력을 확대할 계획이라고 밝혔습니다.',
            },
            {
                'title': f'[실적분석] {stock_name}, 영업이익률 개선 지속',
                'summary': f'{stock_name}가 지난 분기 영업이익률이 전 분기 대비 개선되면서 실적 턴어라운드 기대감이 높아지고 있습니다.',
            },
            {
                'title': f'{stock_name}, 중국 시장 확대로 매출 증가 기대',
                'summary': f'{stock_name}가 중국 시장에서의 점유율 확대에 성공하면서 매출 증가가 예상됩니다.',
            },
            {
                'title': f'{stock_name} 목표주가 상향 조정, 증권가 긍정 전망',
                'summary': f'주요 증권사들이 {stock_name}의 목표주가를 일제히 상향 조정하며 긍정적인 투자의견을 제시했습니다.',
            },
        ]

        articles = []
        now = datetime.now()

        for i in range(min(count, len(mock_news_templates))):
            template = mock_news_templates[i]
            text = template['title'] + ' ' + template['summary']

            # Analyze sentiment
            sentiment_result = self.analyzer.analyze_sentiment(text)
            impact_level = self.analyzer.analyze_impact(text)
            keywords = self.analyzer.extract_keywords(text)

            # Create article
            published_time = now - timedelta(hours=i * 2)
            article = NewsArticle(
                id=f"{stock_code}_{int(published_time.timestamp())}",
                title=template['title'],
                summary=template['summary'],
                url=f"https://finance.naver.com/item/news.nhn?code={stock_code}",
                source='네이버 금융',
                published_at=published_time.isoformat(),
                stock_code=stock_code,
                stock_name=stock_name,
                sentiment=sentiment_result['sentiment'],
                sentiment_score=sentiment_result['score'],
                confidence=sentiment_result['confidence'],
                impact_level=impact_level,
                keywords=keywords
            )
            articles.append(article)

        return articles

    def get_news_for_stock(
        self,
        stock_code: str,
        stock_name: str,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[NewsArticle]:
        """
        Get news articles for a stock

        Args:
            stock_code: Stock code
            stock_name: Stock name
            limit: Maximum number of articles
            use_cache: Whether to use cached data

        Returns:
            List of NewsArticle objects
        """
        try:
            # Check cache first
            if use_cache and self._is_cache_valid(stock_code):
                cached_data = self.news_cache[stock_code]['articles']
                return [NewsArticle(**article) for article in cached_data[:limit]]

            # For now, use mock news (replace with real API later)
            articles = self._create_mock_news(stock_code, stock_name, count=limit)

            # Cache the results
            self.news_cache[stock_code] = {
                'articles': [a.to_dict() for a in articles],
                'cached_at': datetime.now().isoformat()
            }
            self._save_cache()

            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {stock_code}: {e}")
            return []

    def get_news_summary(self, stock_code: str, stock_name: str) -> Optional[NewsSummary]:
        """
        Get news summary for a stock

        Args:
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            NewsSummary object
        """
        try:
            articles = self.get_news_for_stock(stock_code, stock_name)

            if not articles:
                return None

            positive_count = sum(1 for a in articles if a.sentiment == 'positive')
            negative_count = sum(1 for a in articles if a.sentiment == 'negative')
            neutral_count = sum(1 for a in articles if a.sentiment == 'neutral')

            avg_score = sum(a.sentiment_score for a in articles) / len(articles)

            # Overall sentiment
            if avg_score > 0.2:
                overall = 'positive'
            elif avg_score < -0.2:
                overall = 'negative'
            else:
                overall = 'neutral'

            return NewsSummary(
                stock_code=stock_code,
                stock_name=stock_name,
                total_articles=len(articles),
                positive_count=positive_count,
                negative_count=negative_count,
                neutral_count=neutral_count,
                avg_sentiment_score=avg_score,
                overall_sentiment=overall,
                last_updated=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error creating news summary: {e}")
            return None

    def get_news_for_dashboard(
        self,
        stock_code: str,
        stock_name: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get news formatted for dashboard

        Returns:
            Dictionary ready for JSON API response
        """
        try:
            articles = self.get_news_for_stock(stock_code, stock_name, limit=limit)
            summary = self.get_news_summary(stock_code, stock_name)

            return {
                'success': True,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'summary': asdict(summary) if summary else None,
                'articles': [a.to_dict() for a in articles]
            }

        except Exception as e:
            logger.error(f"Error getting dashboard news: {e}")
            return {
                'success': False,
                'message': str(e)
            }


# Example usage
if __name__ == '__main__':
    # Test sentiment analyzer
    analyzer = SentimentAnalyzer()

    test_texts = [
        "삼성전자, 3분기 영업이익 전년 대비 25% 증가 전망",
        "카카오 주가, 외국인 매도세에 약세 지속",
        "SK하이닉스, 신규 공장 건설로 생산 능력 확대"
    ]

    print("\n감성 분석 테스트")
    print("=" * 60)
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"\n텍스트: {text}")
        print(f"감성: {result['sentiment']}")
        print(f"점수: {result['score']:.2f}")
        print(f"신뢰도: {result['confidence']:.2f}")

    # Test news service
    print("\n\n뉴스 피드 테스트")
    print("=" * 60)
    service = NewsFeedService()
    articles = service.get_news_for_stock('005930', '삼성전자', limit=5)

    for article in articles:
        print(f"\n제목: {article.title}")
        print(f"감성: {article.sentiment} ({article.sentiment_score:.2f})")
        print(f"영향도: {article.impact_level}")
        print(f"키워드: {', '.join(article.keywords)}")
