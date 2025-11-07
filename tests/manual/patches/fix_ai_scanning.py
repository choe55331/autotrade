"""
AI 스캐닝 종목 연동 수정 패치
문제: 대시보드에 AI 시스템 스캐닝 종목이 표시되지 않음
해결: scanner_pipeline의 결과를 대시보드에 올바르게 전달
"""

"""
다양한 접근법:
1. approach_1: scanner_pipeline 직접 접근
2. approach_2: scan_progress 업데이트 로직 추가
3. approach_3: 실시간 스캔 상태 반영
4. approach_4: 캐시와 실시간 데이터 결합
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class AIScanningFix:
    """AI 스캐닝 종목 연동 수정"""

    @staticmethod
    def approach_1_direct_pipeline_access(scanner_pipeline) -> Dict[str, Any]:
        """
        접근법 1: scanner_pipeline 직접 접근

        ScannerPipeline 객체에서 직접 결과 가져오기
        가장 정확하고 실시간 데이터
        """
        try:
            if not scanner_pipeline:
                return {
                    'fast_scan': {'count': 0, 'last_run': 'N/A'},
                    'deep_scan': {'count': 0, 'last_run': 'N/A'},
                    'ai_scan': {'count': 0, 'last_run': 'N/A'},
                    'error': 'scanner_pipeline not available'
                }

            fast_results = getattr(scanner_pipeline, 'fast_scan_results', [])
            fast_count = len(fast_results)
            fast_last_run = None
            if hasattr(scanner_pipeline, 'last_fast_scan') and scanner_pipeline.last_fast_scan > 0:
                fast_last_run = datetime.fromtimestamp(scanner_pipeline.last_fast_scan).isoformat()

            deep_results = getattr(scanner_pipeline, 'deep_scan_results', [])
            deep_count = len(deep_results)
            deep_last_run = None
            if hasattr(scanner_pipeline, 'last_deep_scan') and scanner_pipeline.last_deep_scan > 0:
                deep_last_run = datetime.fromtimestamp(scanner_pipeline.last_deep_scan).isoformat()

            ai_results = getattr(scanner_pipeline, 'ai_scan_results', [])
            ai_count = len(ai_results)
            ai_last_run = None
            if hasattr(scanner_pipeline, 'last_ai_scan') and scanner_pipeline.last_ai_scan > 0:
                ai_last_run = datetime.fromtimestamp(scanner_pipeline.last_ai_scan).isoformat()

            return {
                'fast_scan': {
                    'count': fast_count,
                    'last_run': fast_last_run or 'N/A',
                    'results': [
                        {
                            'code': s.code,
                            'name': s.name,
                            'price': s.price,
                            'score': s.fast_scan_score
                        }
                        for s in fast_results[:5]
                    ]
                },
                'deep_scan': {
                    'count': deep_count,
                    'last_run': deep_last_run or 'N/A',
                    'results': [
                        {
                            'code': s.code,
                            'name': s.name,
                            'price': s.price,
                            'score': s.deep_scan_score
                        }
                        for s in deep_results[:5]
                    ]
                },
                'ai_scan': {
                    'count': ai_count,
                    'last_run': ai_last_run or 'N/A',
                    'results': [
                        {
                            'code': s.code,
                            'name': s.name,
                            'price': s.price,
                            'ai_score': s.ai_score,
                            'ai_signal': s.ai_signal
                        }
                        for s in ai_results[:5]
                    ]
                }
            }

        except Exception as e:
            print(f"scanner_pipeline 직접 접근 실패: {e}")
            return {
                'fast_scan': {'count': 0, 'last_run': 'N/A'},
                'deep_scan': {'count': 0, 'last_run': 'N/A'},
                'ai_scan': {'count': 0, 'last_run': 'N/A'},
                'error': str(e)
            }

    @staticmethod
    def approach_2_scan_progress_sync(bot_instance) -> Dict[str, Any]:
        """
        접근법 2: scan_progress 동기화

        scanner_pipeline의 결과를 scan_progress에 동기화
        기존 코드와의 호환성 유지
        """
        try:
            if not bot_instance:
                return {
                    'fast_scan': {'count': 0, 'last_run': 'N/A'},
                    'deep_scan': {'count': 0, 'last_run': 'N/A'},
                    'ai_scan': {'count': 0, 'last_run': 'N/A'},
                    'error': 'bot_instance not available'
                }

            if hasattr(bot_instance, 'scanner_pipeline'):
                pipeline = bot_instance.scanner_pipeline

                if not hasattr(bot_instance, 'scan_progress'):
                    bot_instance.scan_progress = {}

                fast_results = getattr(pipeline, 'fast_scan_results', [])
                bot_instance.scan_progress['top_candidates'] = [
                    {
                        'code': s.code,
                        'name': s.name,
                        'price': s.price,
                        'score': s.fast_scan_score
                    }
                    for s in fast_results
                ]

                deep_results = getattr(pipeline, 'deep_scan_results', [])
                bot_instance.scan_progress['pending_ai_analysis'] = [
                    {
                        'code': s.code,
                        'name': s.name,
                        'price': s.price,
                        'score': s.deep_scan_score
                    }
                    for s in deep_results
                ]

                ai_results = getattr(pipeline, 'ai_scan_results', [])
                bot_instance.scan_progress['approved'] = [
                    {
                        'code': s.code,
                        'name': s.name,
                        'price': s.price,
                        'ai_score': s.ai_score,
                        'ai_signal': s.ai_signal
                    }
                    for s in ai_results
                ]

                fast_count = len(fast_results)
                deep_count = len(deep_results)
                ai_count = len(ai_results)

                return {
                    'fast_scan': {
                        'count': fast_count,
                        'last_run': datetime.fromtimestamp(pipeline.last_fast_scan).isoformat()
                        if hasattr(pipeline, 'last_fast_scan') and pipeline.last_fast_scan > 0
                        else 'N/A'
                    },
                    'deep_scan': {
                        'count': deep_count,
                        'last_run': datetime.fromtimestamp(pipeline.last_deep_scan).isoformat()
                        if hasattr(pipeline, 'last_deep_scan') and pipeline.last_deep_scan > 0
                        else 'N/A'
                    },
                    'ai_scan': {
                        'count': ai_count,
                        'last_run': datetime.fromtimestamp(pipeline.last_ai_scan).isoformat()
                        if hasattr(pipeline, 'last_ai_scan') and pipeline.last_ai_scan > 0
                        else 'N/A'
                    },
                    'synced': True
                }

            elif hasattr(bot_instance, 'scan_progress'):
                scan_progress = bot_instance.scan_progress

                total_candidates = len(scan_progress.get('top_candidates', []))
                ai_reviewed = len(scan_progress.get('approved', [])) + len(scan_progress.get('rejected', []))
                pending = len(scan_progress.get('approved', []))

                return {
                    'fast_scan': {'count': total_candidates, 'last_run': 'N/A'},
                    'deep_scan': {'count': ai_reviewed, 'last_run': 'N/A'},
                    'ai_scan': {'count': pending, 'last_run': 'N/A'},
                    'synced': False
                }

            return {
                'fast_scan': {'count': 0, 'last_run': 'N/A'},
                'deep_scan': {'count': 0, 'last_run': 'N/A'},
                'ai_scan': {'count': 0, 'last_run': 'N/A'},
                'error': 'No data source available'
            }

        except Exception as e:
            print(f"scan_progress 동기화 실패: {e}")
            return {
                'fast_scan': {'count': 0, 'last_run': 'N/A'},
                'deep_scan': {'count': 0, 'last_run': 'N/A'},
                'ai_scan': {'count': 0, 'last_run': 'N/A'},
                'error': str(e)
            }

    @staticmethod
    def approach_3_combined_sources(bot_instance) -> Dict[str, Any]:
        """
        접근법 3: 여러 소스 결합

        scanner_pipeline과 scan_progress 모두 확인
        우선순위: scanner_pipeline > scan_progress
        """
        try:
            result = {
                'fast_scan': {'count': 0, 'last_run': 'N/A'},
                'deep_scan': {'count': 0, 'last_run': 'N/A'},
                'ai_scan': {'count': 0, 'last_run': 'N/A'}
            }

            if hasattr(bot_instance, 'scanner_pipeline'):
                pipeline = bot_instance.scanner_pipeline

                fast_results = getattr(pipeline, 'fast_scan_results', [])
                deep_results = getattr(pipeline, 'deep_scan_results', [])
                ai_results = getattr(pipeline, 'ai_scan_results', [])

                result['fast_scan'] = {
                    'count': len(fast_results),
                    'last_run': datetime.fromtimestamp(pipeline.last_fast_scan).isoformat()
                    if hasattr(pipeline, 'last_fast_scan') and pipeline.last_fast_scan > 0
                    else 'N/A',
                    'source': 'scanner_pipeline'
                }

                result['deep_scan'] = {
                    'count': len(deep_results),
                    'last_run': datetime.fromtimestamp(pipeline.last_deep_scan).isoformat()
                    if hasattr(pipeline, 'last_deep_scan') and pipeline.last_deep_scan > 0
                    else 'N/A',
                    'source': 'scanner_pipeline'
                }

                result['ai_scan'] = {
                    'count': len(ai_results),
                    'last_run': datetime.fromtimestamp(pipeline.last_ai_scan).isoformat()
                    if hasattr(pipeline, 'last_ai_scan') and pipeline.last_ai_scan > 0
                    else 'N/A',
                    'source': 'scanner_pipeline'
                }

            elif hasattr(bot_instance, 'scan_progress'):
                scan_progress = bot_instance.scan_progress

                result['fast_scan'] = {
                    'count': len(scan_progress.get('top_candidates', [])),
                    'last_run': 'N/A',
                    'source': 'scan_progress'
                }

                result['deep_scan'] = {
                    'count': len(scan_progress.get('approved', [])) + len(scan_progress.get('rejected', [])),
                    'last_run': 'N/A',
                    'source': 'scan_progress'
                }

                result['ai_scan'] = {
                    'count': len(scan_progress.get('approved', [])),
                    'last_run': 'N/A',
                    'source': 'scan_progress'
                }

            return result

        except Exception as e:
            print(f"combined sources 실패: {e}")
            return {
                'fast_scan': {'count': 0, 'last_run': 'N/A'},
                'deep_scan': {'count': 0, 'last_run': 'N/A'},
                'ai_scan': {'count': 0, 'last_run': 'N/A'},
                'error': str(e)
            }

    @staticmethod
    def approach_4_realtime_trigger(bot_instance, force_scan: bool = False) -> Dict[str, Any]:
        """
        접근법 4: 실시간 스캔 트리거

        대시보드 조회 시 필요하면 스캔 실행
        """
        try:
            if not bot_instance or not hasattr(bot_instance, 'scanner_pipeline'):
                return {
                    'fast_scan': {'count': 0, 'last_run': 'N/A'},
                    'deep_scan': {'count': 0, 'last_run': 'N/A'},
                    'ai_scan': {'count': 0, 'last_run': 'N/A'},
                    'error': 'scanner_pipeline not available'
                }

            pipeline = bot_instance.scanner_pipeline

            if force_scan or pipeline.should_run_fast_scan():
                print("[SEARCH] Fast Scan 실행...")
                pipeline.run_fast_scan()

            if force_scan or pipeline.should_run_deep_scan():
                if len(pipeline.fast_scan_results) > 0:
                    print("[SEARCH] Deep Scan 실행...")
                    pipeline.run_deep_scan()

            fast_results = getattr(pipeline, 'fast_scan_results', [])
            deep_results = getattr(pipeline, 'deep_scan_results', [])
            ai_results = getattr(pipeline, 'ai_scan_results', [])

            return {
                'fast_scan': {
                    'count': len(fast_results),
                    'last_run': datetime.fromtimestamp(pipeline.last_fast_scan).isoformat()
                    if hasattr(pipeline, 'last_fast_scan') and pipeline.last_fast_scan > 0
                    else 'N/A'
                },
                'deep_scan': {
                    'count': len(deep_results),
                    'last_run': datetime.fromtimestamp(pipeline.last_deep_scan).isoformat()
                    if hasattr(pipeline, 'last_deep_scan') and pipeline.last_deep_scan > 0
                    else 'N/A'
                },
                'ai_scan': {
                    'count': len(ai_results),
                    'last_run': datetime.fromtimestamp(pipeline.last_ai_scan).isoformat()
                    if hasattr(pipeline, 'last_ai_scan') and pipeline.last_ai_scan > 0
                    else 'N/A'
                },
                'triggered': force_scan or pipeline.should_run_fast_scan() or pipeline.should_run_deep_scan()
            }

        except Exception as e:
            print(f"realtime trigger 실패: {e}")
            return {
                'fast_scan': {'count': 0, 'last_run': 'N/A'},
                'deep_scan': {'count': 0, 'last_run': 'N/A'},
                'ai_scan': {'count': 0, 'last_run': 'N/A'},
                'error': str(e)
            }



def get_system_status_fixed_approach_1(bot_instance):
    """
    수정된 get_system_status() - 접근법 1

    dashboard/app_apple.py의 /api/system 엔드포인트 수정
    scanner_pipeline 직접 접근
    """

    scanning_info = AIScanningFix.approach_1_direct_pipeline_access(
        bot_instance.scanner_pipeline if hasattr(bot_instance, 'scanner_pipeline') else None
    )

    return {
        'scanning': scanning_info
    }


def get_system_status_fixed_approach_3(bot_instance):
    """
    수정된 get_system_status() - 접근법 3 (추천)

    scanner_pipeline과 scan_progress 결합
    가장 견고한 방법
    """
    scanning_info = AIScanningFix.approach_3_combined_sources(bot_instance)

    return {
        'scanning': scanning_info
    }



def get_scanning_info(bot_instance, method: str = 'combined') -> Dict[str, Any]:
    """
    스캐닝 정보 조회 (편의 함수)

    Args:
        bot_instance: 봇 인스턴스
        method: 'direct', 'sync', 'combined', 'realtime'

    Returns:
        스캐닝 정보
    """
    if method == 'direct':
        scanner_pipeline = getattr(bot_instance, 'scanner_pipeline', None)
        return AIScanningFix.approach_1_direct_pipeline_access(scanner_pipeline)

    elif method == 'sync':
        return AIScanningFix.approach_2_scan_progress_sync(bot_instance)

    elif method == 'combined':
        return AIScanningFix.approach_3_combined_sources(bot_instance)

    elif method == 'realtime':
        return AIScanningFix.approach_4_realtime_trigger(bot_instance, force_scan=False)

    else:
        raise ValueError(f"Unknown method: {method}")



if __name__ == "__main__":
    print("AI 스캐닝 종목 연동 수정 패치")
    print()
    print("사용법:")
    print("1. 접근법 1: scanner_pipeline 직접 접근")
    print("   info = AIScanningFix.approach_1_direct_pipeline_access(bot.scanner_pipeline)")
    print()
    print("2. 접근법 2: scan_progress 동기화")
    print("   info = AIScanningFix.approach_2_scan_progress_sync(bot)")
    print()
    print("3. 접근법 3 (추천): 여러 소스 결합")
    print("   info = AIScanningFix.approach_3_combined_sources(bot)")
    print()
    print("4. 편의 함수:")
    print("   info = get_scanning_info(bot, method='combined')")
    print()
    print("대시보드 적용:")
    print("  dashboard/app_apple.py의 /api/system 엔드포인트에")
    print("  AIScanningFix.approach_3_combined_sources(bot_instance) 사용")
