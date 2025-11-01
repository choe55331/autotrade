# comprehensive_api_debugger.py (v1.0 - Full Implementation)
import sys
import logging
import json
import datetime
import traceback
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
                             QTextEdit, QLabel, QGridLayout, QLineEdit, QTabWidget,
                             QScrollArea, QHBoxLayout, QCheckBox, QMessageBox, QDateEdit,
                             QSpacerItem, QSizePolicy) # QDateEdit, QSpacerItem, QSizePolicy 추가
from PyQt5.QtCore import QObject, pyqtSlot, QRunnable, QThreadPool, pyqtSignal, QTimer, QDate # QDate 추가
from PyQt5 import QtGui
from typing import Dict, Any, Optional, List, Tuple, Set

# --- 기존 모듈 Import ---
try:
    import kiwoom # Kiwoom 클라이언트 (v2.7+ 권장)
    import config # 설정값 (API 키 등)
    import account # API 정의 (account.py v2.6+ 권장)
except ImportError as e:
    print(f"오류: 필수 모듈(kiwoom.py, config.py, account.py)을 찾을 수 없습니다. {e}")
    sys.exit()

# --- 로깅 설정 ---
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] (Comp-Debugger) %(message)s", datefmt="%H:%M:%S")
logging.getLogger("kiwoom").name = "API.Client" # kiwoom 로거 이름 변경

# --- Worker (백그라운드 API 호출 담당) ---
class WorkerSignals(QObject):
    # 결과 리스트, API ID(suffix포함), 테스트명, 총 variant 수
    api_id_finished = pyqtSignal(list, str, str, int)

class Worker(QRunnable):
    def __init__(self, request_func, api_id_base, api_id_with_suffix, test_name, variants: List[Tuple[str, Dict[str, Any]]]):
        super().__init__()
        self.request_func = request_func
        self.api_id_base = api_id_base
        self.api_id_with_suffix = api_id_with_suffix
        self.test_name = test_name
        self.variants = variants
        self.signals = WorkerSignals()
        self.logger = logging.getLogger("Comp-Debugger.Worker")

    def run(self):
        # rest_api_debugger.py v2.7의 Worker.run() 로직과 동일
        # kiwoom.py v2.7+ 의 오류 딕셔너리 반환 처리가 포함된 버전 사용
        all_variant_results = []
        total_variants = len(self.variants)
        self.logger.debug(f"[{self.api_id_with_suffix}] Worker 시작 ({total_variants} variants)...")

        path_map = {}
        # request_func가 KiwoomRESTClient의 메서드일 경우 path_map 가져오기
        if hasattr(self.request_func, '__self__') and self.request_func.__self__ is not None:
             client_instance = self.request_func.__self__
             path_map = getattr(client_instance, 'path_map', {})
             if not isinstance(path_map, dict): path_map = {}

        for i, (path_prefix, body) in enumerate(self.variants):
            variant_idx = i + 1; variant_tuple = (path_prefix, body)
            result_status = "unknown"; result_data = None # 성공 dict 또는 오류 dict/tuple 저장

            # --- 경로 유효성 검사 ---
            if path_prefix not in path_map:
                 error_msg = f"경로 오류: '{path_prefix}'가 kiwoom.py path_map에 정의되지 않음."
                 self.logger.warning(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 건너뜀: {error_msg}")
                 result_status = "path_error"
                 result_data = (path_prefix, body, error_msg, None) # 오류 정보 튜플
                 all_variant_results.append((result_status, result_data, variant_tuple, variant_idx))
                 continue # 다음 variant 처리

            self.logger.debug(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 시도: Path='{path_prefix}', Body={json.dumps(body, ensure_ascii=False, indent=None)}")
            try:
                # --- API 호출 ---
                if hasattr(self.request_func, '__self__') and self.request_func.__self__ is not None:
                     result = self.request_func(api_id=self.api_id_base, body=body, path_prefix=path_prefix)
                else: # Singleton 패턴에서는 거의 발생 안 함
                     self.logger.error(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 실패: 클라이언트 인스턴스 없음.")
                     result = {"return_code": -105, "return_msg": "클라이언트 인스턴스 없이 요청됨"}

                # time.sleep(0.05) # 매우 짧은 지연 (선택적)

                # --- 결과 분석 ---
                if isinstance(result, dict):
                    rc = result.get('return_code'); rm = result.get('return_msg', '')

                    if rc == 0: # 성공
                        # 데이터 존재 여부 확인 (list 또는 non-empty/non-zero 단일 값)
                        list_keys = [k for k, v in result.items() if isinstance(v, list) and k not in ['return_code', 'return_msg']]
                        single_keys = [k for k, v in result.items() if not isinstance(v, list) and k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
                        empty_vals = [None, "", "0", "0.00", "0.0", 0, 0.0, "000000000000000", "N/A", [], {}] # 빈 값 정의 확장
                        has_list = any(len(result.get(k, [])) > 0 for k in list_keys)
                        has_single = any((v_strip := (v.strip() if isinstance(v, str) else v)) not in empty_vals for k in single_keys if (v := result.get(k)) is not None)

                        if has_list or has_single:
                            self.logger.debug(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 성공 (Code 0, 데이터 확인).")
                            result_status = "success"; result_data = result # 성공 dict 저장
                        else: # Code 0 이나 데이터 없음
                            no_data_msgs = ["조회 결과가 없습니다", "조회된 내역이 없습니다", "데이터가 없습니다", "해당 내역이 없습니다"]
                            reason = f"정상 (Code 0), 데이터 없음 ({'API 메시지: ' + rm if any(m in rm for m in no_data_msgs) else '유의미 데이터 없음'})"
                            self.logger.debug(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] {reason} (Path: {path_prefix})")
                            result_status = "no_data"; result_data = result # 결과 dict 저장
                    elif rc == 20: # 가정: 20이 '데이터 없음' 코드 (실제 응답 기반 확인 필요)
                        self.logger.debug(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] API No Data: {rm} (Code: {rc}) (Path: {path_prefix})")
                        result_status = "no_data"; result_data = result # 결과 dict 저장
                    elif rc is not None: # 다른 API 오류 코드
                        self.logger.debug(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 실패: API Logic Error: {rm} (Code: {rc}) (Path: {path_prefix})")
                        result_status = "api_error"; result_data = result # 오류 dict 저장
                    else: # return_code 없는 딕셔너리 (거의 발생 안 함)
                        self.logger.warning(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 실패: Unexpected Dict (No RC): {str(result)[:100]}... (Path: {path_prefix})")
                        result_status = "exception"; result_data = (path_prefix, body, "Unexpected Dict (No RC)", None)
                else: # 딕셔너리 아닌 결과 (거의 발생 안 함)
                    self.logger.error(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 실패: Unexpected Result Type: {type(result)} (Path: {path_prefix})")
                    result_status = "exception"; result_data = (path_prefix, body, f"Unexpected Result Type: {type(result)}", None)

            # --- 예외 처리 ---
            except Exception as e:
                error_msg = f"요청 중 예외 발생: {e.__class__.__name__}: {e}"
                self.logger.error(f"[{self.api_id_with_suffix} Var {variant_idx}/{total_variants}] 예외 발생 (Path: {path_prefix}): {e}", exc_info=False) # 상세 traceback은 DEBUG로
                self.logger.debug(traceback.format_exc()) # DEBUG 레벨로 traceback 기록
                result_status = "exception"
                result_data = (path_prefix, body, error_msg, traceback.format_exc(limit=1)) # 오류 정보 튜플

            # 현재 variant 결과 추가
            all_variant_results.append((result_status, result_data, variant_tuple, variant_idx))

        # --- 모든 Variant 처리 후 신호 발생 ---
        self.logger.debug(f"[{self.api_id_with_suffix}] Worker 완료. 신호 발생.")
        self.signals.api_id_finished.emit(all_variant_results, self.api_id_with_suffix, self.test_name, total_variants)


# --- 메인 윈도우 ---
class ComprehensiveDebuggerWindow(QMainWindow):
    # API ID와 한글 이름 매핑 (account.py 파싱 실패 시 대비)
    DEFAULT_API_NAMES = {"ka10001": "주식기본정보", "kt00018": "계좌평가잔고"}

    def __init__(self):
        super().__init__()
        self.api_client = None
        self.threadpool = QThreadPool()
        self.client_init_success = False
        self.api_definitions_cache = {} # API 이름 캐시
        self.api_buttons = {} # API ID와 버튼 위젯 매핑 {api_id_with_suffix: QPushButton}
        self.current_test_api_id = None # 현재 실행 중인 API ID 추적용

        self.init_ui() # 기본 UI 구조 생성
        self.init_api_client_sync() # API 클라이언트 동기 초기화
        self._cache_api_names() # account.py에서 API 한글 이름 가져오기
        self._create_input_widgets() # 종목코드, 날짜 등 입력 위젯 생성
        self._create_tabs_and_buttons() # API 호출 버튼 탭 생성
        self.update_ui_after_init() # 클라이언트 상태에 따라 UI 업데이트

        self.log("종합 API 디버거 v1.0 시작.")
        self.log("account.py 와 kiwoom.py 의 최신 버전을 사용해야 합니다.")

    def log(self, msg, level="INFO"):
        # 기존 rest_api_debugger.py의 log 함수와 동일
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {msg}"
        color_map = {"DEBUG": "gray", "INFO": "black", "WARNING": "orange", "ERROR": "red", "CRITICAL": "purple"}
        color = color_map.get(level, "black")
        should_log_to_ui = True
        if level == "DEBUG":
            logging.debug(msg)
            should_log_to_ui = hasattr(self, 'show_details_checkbox') and self.show_details_checkbox.isChecked()
        else:
            if level == "WARNING": logging.warning(msg)
            elif level == "ERROR": logging.error(msg)
            elif level == "CRITICAL": logging.critical(msg)
            else: logging.info(msg)

        if should_log_to_ui and hasattr(self, 'log_output'):
            log_entry_escaped = log_entry.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.log_output.append(f'<font color="{color}">{log_entry_escaped}</font>')
            scrollbar = self.log_output.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum()) # 항상 맨 아래로 스크롤
        elif not hasattr(self, 'log_output'):
             print(log_entry) # UI 생성 전
        QApplication.processEvents() # UI 업데이트 강제

    def init_ui(self):
        # 기본 창 설정
        self.setWindowTitle("종합 Kiwoom REST API 디버거 (v1.0)")
        self.setGeometry(100, 100, 1200, 800)

        # 중앙 위젯 및 레이아웃
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget) # 좌우 분할

        # --- 왼쪽 패널 (입력 + API 버튼) ---
        left_panel = QWidget(); left_panel.setFixedWidth(450)
        left_layout = QVBoxLayout(left_panel); main_layout.addWidget(left_panel)

        # API 상태 라벨 (상단 고정)
        self.api_status_label = QLabel("API 클라이언트: -")
        self.api_status_label.setStyleSheet("padding: 5px; border: 1px solid gray; background-color: #f0f0f0;")
        left_layout.addWidget(self.api_status_label)

        # 입력 위젯 영역 (스크롤 가능)
        input_scroll = QScrollArea(); input_scroll.setWidgetResizable(True)
        input_scroll_content = QWidget(); input_scroll.setWidget(input_scroll_content)
        self.input_layout = QGridLayout(input_scroll_content) # Grid 사용
        input_scroll.setFixedHeight(250) # 입력 영역 높이 고정
        left_layout.addWidget(input_scroll)

        # API 버튼 탭 영역 (나머지 공간 차지)
        self.api_tabs = QTabWidget()
        left_layout.addWidget(self.api_tabs)

        # 상세 로그 보기 체크박스 (하단 고정)
        self.show_details_checkbox = QCheckBox("상세 데이터/오류 로그 보기 (성공 시 전체)")
        left_layout.addWidget(self.show_details_checkbox)

        # --- 오른쪽 패널 (결과 로그) ---
        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel); main_layout.addWidget(right_panel)
        right_layout.addWidget(QLabel("<b>결과 로그 (API 호출 결과 및 데이터 요약)</b>"))
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True)
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont); font.setPointSize(9)
        self.log_output.setFont(font); right_layout.addWidget(self.log_output)

    def init_api_client_sync(self):
        """ API 클라이언트를 동기적으로 초기화하고 상태를 업데이트합니다. """
        self.log("API 클라이언트(Singleton) 초기화 시도...")
        try:
            self.api_client = kiwoom.KiwoomRESTClient()
            if not all([config.KIWOOM_REST_APPKEY, config.KIWOOM_REST_SECRETKEY, config.ACCOUNT_NUMBER, config.KIWOOM_REST_BASE_URL]):
                 self.log("config.py에 API URL, 키 또는 계좌번호가 없습니다.", "CRITICAL")
                 self.client_init_success = False; self.update_ui_after_init(); return

            if self.api_client.token and self.api_client.last_error_msg is None:
                self.log("✅ API 클라이언트 준비 완료 (초기 토큰 발급 성공)")
                self.client_init_success = True
                # Path check (optional, for advanced debugging)
                path_map = getattr(self.api_client, 'path_map', {}); required_paths = {'acnt', 'ordr', 'stkinfo', 'mrkcond', 'chart', 'rkinfo', 'frgnistt', 'sect', 'thme', 'slb', 'etf', 'elw'}
                missing_paths = list(required_paths - set(path_map.keys()))
                if missing_paths: self.log(f"⚠️ 경고: kiwoom.py path_map 누락: {', '.join(sorted(missing_paths))}. 해당 경로 API 실패 예상.", "WARNING")
            else:
                err_msg = getattr(self.api_client, 'last_error_msg', "알 수 없는 토큰 오류")
                self.log(f"❌ API 클라이언트 초기화 실패 (초기 토큰 발급 실패): {err_msg}", "ERROR")
                self.client_init_success = False
        except Exception as e:
            self.log(f"❌ API 클라이언트 초기화 중 치명적 오류: {e}", "CRITICAL"); self.log(traceback.format_exc(), "DEBUG")
            self.client_init_success = False
        self.update_ui_after_init() # UI 업데이트 호출

    def _cache_api_names(self):
        # 기존 rest_api_debugger.py의 _cache_api_names 함수와 동일
        import inspect
        self.api_definitions_cache = self.DEFAULT_API_NAMES.copy() # 기본값 포함 시작
        try:
            source_lines, _ = inspect.getsourcelines(account.get_api_definition)
            dict_start_index = -1; dict_end_index = -1; bracket_level = 0; in_dict = False
            for i, line in enumerate(source_lines):
                stripped_line = line.strip()
                if stripped_line.startswith('definitions: Dict[str, VariantFunc] = {'):
                    dict_start_index = i; in_dict = True; bracket_level += line.count('{') - line.count('}'); continue
                if in_dict:
                    bracket_level += line.count('{') - line.count('}')
                    if bracket_level <= 0: dict_end_index = i; break
            if dict_start_index == -1 or dict_end_index == -1: self.log("Warning: account.py에서 'definitions' 딕셔너리를 찾을 수 없음.", "WARNING"); return

            current_id = None
            for line_num, line in enumerate(source_lines[dict_start_index + 1 : dict_end_index]):
                stripped_line = line.strip()
                if stripped_line.startswith('"') and '": lambda p:' in stripped_line:
                    parts = stripped_line.split('"'); current_id = parts[1] if len(parts) > 1 else None
                    if current_id and '#' in stripped_line: # ID 라인에 주석이 있으면 이름 추출
                         comment_part = stripped_line.split('#', 1)[-1].strip()
                         name_part = comment_part.split('(', 1)[0].strip() # 괄호 이전까지 추출
                         if any('\uac00' <= char <= '\ud7a3' for char in name_part): # 한글 포함 확인
                             self.api_definitions_cache[current_id] = name_part; current_id = None; continue
                # ID 라인에 주석 없을 때 -> 이전 라인 주석 확인 (더 안전하게)
                elif current_id and stripped_line.startswith('#'):
                     prev_line_num = dict_start_index + 1 + line_num -1
                     if prev_line_num > dict_start_index:
                         prev_line_stripped = source_lines[prev_line_num].strip()
                         if prev_line_stripped.startswith('#'):
                             comment_part = prev_line_stripped.split('#', 1)[-1].strip()
                             name_part = comment_part.split('(', 1)[0].strip()
                             if any('\uac00' <= char <= '\ud7a3' for char in name_part):
                                 self.api_definitions_cache[current_id] = name_part; current_id = None; continue # 이전 줄에서 찾으면 current_id 초기화
                # 라인 끝 처리 (이름 못 찾았으면 ID로 대체)
                if stripped_line.endswith(',') or stripped_line.endswith('],'):
                    if current_id and current_id not in self.api_definitions_cache:
                        self.api_definitions_cache[current_id] = current_id # Fallback
                    current_id = None # 다음 ID 처리 위해 초기화
            if current_id and current_id not in self.api_definitions_cache: self.api_definitions_cache[current_id] = current_id # 마지막 ID 처리
            self.log(f"account.py에서 {len(self.api_definitions_cache)}개 API 이름 로드 완료.")
        except Exception as e: self.log(f"Warning: account.py API 이름 파싱 오류: {e}", "WARNING"); self.api_definitions_cache = self.DEFAULT_API_NAMES.copy()


    def _create_input_widgets(self):
        """ 입력 위젯들을 생성하고 레이아웃에 추가합니다. """
        layout = self.input_layout # Grid Layout 사용

        # 행 번호 관리
        row = 0

        # --- [신규] 모든 테스트 실행 버튼 ---
        self.run_all_btn = QPushButton("▶ 모든 조회 테스트 실행 (주문 제외)")
        self.run_all_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.run_all_btn.clicked.connect(self.run_all_tests)
        self.run_all_btn.setEnabled(False) # 초기 비활성화
        # Grid layout의 첫 행에 넓게 배치 (4열 사용)
        layout.addWidget(self.run_all_btn, row, 0, 1, 4) # <--- 이 부분이 버튼을 추가합니다.
        row += 1
        # --- [신규] 버튼 추가 완료 ---

        # 기본 입력 (종목, 수량, 가격)
        layout.addWidget(QLabel("종목코드 (주식):"), row, 0); self.code_input = QLineEdit(account.p_common.get("placeholder_stk_kospi","147830")); layout.addWidget(self.code_input, row, 1)
        layout.addWidget(QLabel("주문수량:"), row, 2); self.qty_input = QLineEdit("1"); layout.addWidget(self.qty_input, row, 3)
        row += 1
        layout.addWidget(QLabel("주문가격 (지정가):"), row, 0); self.price_input = QLineEdit("10000"); layout.addWidget(self.price_input, row, 1)
        layout.addWidget(QLabel("원주문번호:"), row, 2); self.orig_ord_no_input = QLineEdit(account.p_common.get("dummy_order_id","0000000")); layout.addWidget(self.orig_ord_no_input, row, 3)
        row += 1

        # 날짜 입력 (시작일, 종료일)
        layout.addWidget(QLabel("시작일:"), row, 0); self.start_date_input = QDateEdit(QDate.currentDate().addDays(-7)); self.start_date_input.setCalendarPopup(True); self.start_date_input.setDisplayFormat("yyyyMMdd"); layout.addWidget(self.start_date_input, row, 1)
        layout.addWidget(QLabel("종료일/기준일:"), row, 2); self.end_date_input = QDateEdit(QDate.currentDate()); self.end_date_input.setCalendarPopup(True); self.end_date_input.setDisplayFormat("yyyyMMdd"); layout.addWidget(self.end_date_input, row, 3)
        row += 1

        # 추가 코드 입력 (ETF, ELW, 금)
        layout.addWidget(QLabel("ETF코드:"), row, 0); self.etf_code_input = QLineEdit(account.p_common.get("placeholder_etf","069500")); layout.addWidget(self.etf_code_input, row, 1)
        layout.addWidget(QLabel("ELW코드:"), row, 2); self.elw_code_input = QLineEdit(account.p_common.get("placeholder_elw","57JBHH")); layout.addWidget(self.elw_code_input, row, 3)
        row += 1
        layout.addWidget(QLabel("금현물코드:"), row, 0); self.gold_code_input = QLineEdit(account.p_common.get("placeholder_gold","M04020000")); layout.addWidget(self.gold_code_input, row, 1)
        layout.addWidget(QLabel("조건검색 Seq:"), row, 2); self.cond_seq_input = QLineEdit(account.p_common.get("dummy_seq","0")); layout.addWidget(self.cond_seq_input, row, 3)
        row += 1

        # 업종/테마 코드 입력
        layout.addWidget(QLabel("업종코드:"), row, 0); self.inds_code_input = QLineEdit(account.p_common.get("placeholder_inds","001")); layout.addWidget(self.inds_code_input, row, 1)
        layout.addWidget(QLabel("테마코드:"), row, 2); self.thema_code_input = QLineEdit(account.p_common.get("placeholder_thema","100")); layout.addWidget(self.thema_code_input, row, 3)
        row += 1

        # 입력 필드 간격 조정
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        # 마지막 행 아래에 여백 추가 (선택적)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0)


    def _create_tabs_and_buttons(self):
        """ API 호출 버튼들을 생성하고 탭에 추가합니다. """
        self.api_buttons = {} # 버튼 딕셔너리 초기화

        # 탭 생성 함수
        def create_tab(title):
            tab = QWidget()
            scroll = QScrollArea(); scroll.setWidgetResizable(True)
            scroll_content = QWidget(); scroll.setWidget(scroll_content)
            layout = QVBoxLayout(scroll_content)
            layout.setSpacing(3) # 버튼 간격 줄임
            layout.setContentsMargins(5, 5, 5, 5) # 내부 여백 줄임
            # 제목 라벨 (선택적)
            # title_label = QLabel(f"<b>--- {title} ---</b>")
            # title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            # layout.addWidget(title_label)
            tab_layout = QVBoxLayout(tab); tab_layout.addWidget(scroll); tab_layout.setContentsMargins(0,0,0,0)
            return tab, layout

        # 탭 정의 (카테고리별)
        tabs_config = {
            "💳 계좌": ["kt00005", "kt00018", "ka10085", "ka10075", "ka10076", "kt00001", "kt00004", "kt00010", "kt00011", "kt00012", "kt00013", "ka10077", "ka10074", "ka10073", "ka10072", "ka01690", "kt00007", "kt00009", "kt00015", "kt00017", "kt00002", "kt00003", "kt00008", "kt00016", "ka10088", "ka10170"],
            "📈 기본시세": ["ka10001", "ka10004", "ka10003", "ka10007", "ka10087", "ka10006", "ka10005"],
            "📊 상세시세/분석": ["ka10059", "ka10061", "ka10015", "ka10043", "ka10002", "ka10013", "ka10025", "ka10026", "ka10045", "ka10046", "ka10047", "ka10052", "ka10054", "ka10055", "ka10063", "ka10066", "ka10078", "ka10086", "ka10095", "ka10099", "ka10100", "ka10101", "ka10102", "ka10084"],
            "📉 차트": ["ka10079", "ka10080", "ka10081", "ka10082", "ka10083", "ka10094", "ka10060", "ka10064"],
            "🏆 기본순위": ["ka10027", "ka10017", "ka10032", "ka10031", "ka10023", "ka10016", "ka00198"],
            "🏅 상세순위": ["ka10020", "ka10021", "ka10022", "ka10019", "ka10028", "ka10018", "ka10029", "ka10033", "ka10098"],
            "🏭 업종/테마": ["ka20001", "ka20002", "ka20003", "ka20009", "ka10010", "ka10051", "ka90001", "ka90002"],
            "👥 수급/대차": ["ka10008", "ka10009", "ka10131", "ka10034", "ka10035", "ka10036", "ka10037", "ka10038", "ka10039", "ka10040", "ka10042", "ka10053", "ka10058", "ka10062", "ka10065", "ka90009", "ka90004", "ka90005", "ka90007", "ka90008", "ka90013", "ka10014", "ka10068", "ka10069", "ka20068", "ka90012"], # 수급 + 대차 + 프로그램
            "✨ ELW/ETF/금": ["ka10048", "ka10050", "ka30001", "ka30002", "ka30003", "ka30004", "ka30005", "ka30009", "ka30010", "ka30011", "ka30012", "ka40001", "ka40002", "ka40003", "ka40004", "ka40006", "ka40007", "ka40008", "ka40009", "ka40010", "ka50010", "ka50012", "ka50087", "ka50100", "ka50101", "ka52301", "kt50020", "kt50021", "kt50030", "kt50031", "kt50032", "kt50075"], # ELW + ETF + 금 시세/계좌
            "🚨 주문(개별)": ["kt10000", "kt10001", "kt10002", "kt10003", "kt10006", "kt10007", "kt10008", "kt10009", "kt50000", "kt50001", "kt50002", "kt50003"],
            "🔍 조건검색(WS)": ["ka10171", "ka10172", "ka10173", "ka10174"] # WebSocket API
        }

        # 탭 및 버튼 생성
        for tab_title, api_ids in tabs_config.items():
            tab_widget, tab_layout = create_tab(tab_title)
            self.api_tabs.addTab(tab_widget, tab_title)

            # 주문 탭 경고 추가
            if "주문" in tab_title:
                warning_label = QLabel("<b>🚨 실제 주문/정정/취소 실행! 모의투자 확인! 🚨</b>"); warning_label.setStyleSheet("color: red; background-color: #fff0f0; border: 1px solid red; padding: 5px;"); tab_layout.addWidget(warning_label)

            # API 버튼 추가
            for api_id in api_ids:
                self._add_test_button(tab_layout, api_id, None) # 기본 Variant 사용

            tab_layout.addStretch() # 버튼 위로 정렬

    def _add_test_button(self, layout, api_id_with_suffix, variants_func):
        """ 레이아웃에 테스트 버튼을 추가하고 관리 목록에 저장합니다. """
        base_api_id = api_id_with_suffix.split('_')[0]
        # account.py 파싱 결과 또는 기본 이름 사용
        test_name = self.api_definitions_cache.get(base_api_id, base_api_id)
        # 버튼 텍스트 생성 (API ID + 이름)
        button_text = f"{api_id_with_suffix}: {test_name}"
        # 버튼 생성 및 시그널 연결
        btn = QPushButton(button_text)
        btn.clicked.connect(lambda checked, a=api_id_with_suffix, vf=variants_func, tn=test_name:
                            self.run_single_test_wrapper(a, tn, vf))
        layout.addWidget(btn)
        btn.setEnabled(False) # 초기에는 비활성화
        self.api_buttons[api_id_with_suffix] = btn # 버튼 관리 목록에 추가

    def run_all_tests(self):
        """ 모든 조회성 API 테스트를 순차적으로 실행합니다. """
        if not self.client_init_success or not self.api_client:
            self.log("API 클라이언트가 준비되지 않아 '모든 테스트 실행'을 시작할 수 없습니다.", "ERROR"); return
        # 이미 실행 중이면 중단 처리
        if hasattr(self, 'is_running_all') and self.is_running_all:
            self.is_running_all = False # 플래그 변경
            self.log("ℹ️ 모든 테스트 실행 중단됨.", "WARNING")
            self.run_all_btn.setText("▶ 모든 조회 테스트 실행 (주문 제외)") # 버튼 텍스트 복원
            # 모든 버튼 활성화 (API 상태에 따라)
            self.update_ui_after_init()
            # 큐 비우기 (더 이상 실행 안 함)
            if hasattr(self, 'test_queue'): self.test_queue = []
            return

        # 테스트 시작 준비
        common_params = self._get_common_params()
        self.test_queue = [] # 실행할 테스트 큐 초기화
        self.test_results = [] # 결과 저장 리스트 초기화
        self.is_running_all = True # 실행 플래그 설정
        self.log_output.clear() # 로그 창 비우기
        self.log("--- 🚀 모든 조회 API 테스트 시작 ---")

        # 버튼 비활성화
        for btn in self.api_buttons.values(): btn.setEnabled(False)
        self.run_all_btn.setText("■ 테스트 중지") # 버튼 텍스트 변경
        self.run_all_btn.setEnabled(True) # 중지 버튼은 활성화

        total_variants_to_run = 0
        skipped_api_count = 0
        prepare_failed_count = 0

        # 제외할 API ID 목록 (주문, WS, 실시간 등)
        exclude_api_ids_base = {
            "kt10000", "kt10001", "kt10002", "kt10003", "kt10006", "kt10007", "kt10008", "kt10009", # 주식/신용 주문
            "kt50000", "kt50001", "kt50002", "kt50003", # 금현물 주문
            "ka10171", "ka10172", "ka10173", "ka10174", # 조건검색 WS
            "00","04","0A","0B","0C","0D","0E","0F","0G","0H","OI","OJ","OU","0g","Om","Os","Ou","Ow","1h" # 실시간 등록 ID
        }

        # api_buttons 딕셔너리를 순회하며 테스트 큐 생성
        for api_id_with_suffix, btn_widget in self.api_buttons.items():
            base_api_id = api_id_with_suffix.split('_')[0]
            test_name = self.api_definitions_cache.get(base_api_id, base_api_id)
            reason = ""

            # 제외 대상 확인
            if base_api_id in exclude_api_ids_base:
                reason = "자동 실행 시 제외 (주문/WS/실시간 API)"
                self.test_results.append({"api_id": api_id_with_suffix, "name": test_name, "status": "⚪ 건너뜀", "reason": reason, "details": None, "variant_idx": 1, "total_variants": 1})
                skipped_api_count += 1
                continue

            # Variant 생성 시도 (run_single_test_wrapper 로직 참고)
            try:
                variants = None
                # variants_func를 직접 가져올 수 없으므로, account.py를 통해 가져옴
                func = account.get_api_definition(base_api_id)
                if func: variants = func(common_params)

                if variants is None:
                    reason = f"'{base_api_id}' 정의 없음/None 반환."
                elif not isinstance(variants, list):
                    reason = "Variants 결과가 리스트가 아님"
                elif not variants: # 빈 리스트 [] -> 건너뛰기
                    reason = "account.py 정의 비어있음 (의도된 건너뜀)"
                    # 로그 없이 결과만 기록
                    self.test_results.append({"api_id": api_id_with_suffix, "name": test_name, "status": "⚪ 건너뜀", "reason": reason, "details": None, "variant_idx": 1, "total_variants": 1})
                    skipped_api_count += 1
                    continue # 다음 버튼으로

                # 오류 없이 Variant 생성 성공 -> 큐에 추가
                if not reason:
                    self.test_queue.append((base_api_id, test_name, variants, api_id_with_suffix))
                    total_variants_to_run += len(variants)
                    continue # 다음 버튼으로

            except Exception as e: # Variant 생성 중 예외 발생
                 reason = f"Variants 생성 오류: {e.__class__.__name__}: {e}"
                 self.log(f"❌ '{api_id_with_suffix}: {test_name}' 준비 중 {reason}. 건너뜀.\n{traceback.format_exc()}", "ERROR")

            # 오류 발생 시 결과 기록
            self.test_results.append({"api_id": api_id_with_suffix, "name": test_name, "status": "❌ 실패 (준비)", "reason": reason, "details": traceback.format_exc() if 'e' in locals() else None, "variant_idx": 0, "total_variants": 0})
            prepare_failed_count += 1

        # 큐 생성 완료 후 실행 시작
        if not self.test_queue:
            self.log(f"실행할 테스트 케이스 없음 ({skipped_api_count}개 API 건너뜀, {prepare_failed_count}개 API 준비실패).", "WARNING")
            self.is_running_all = False # 플래그 리셋
            self.run_all_btn.setText("▶ 모든 조회 테스트 실행 (주문 제외)")
            self.update_ui_after_init() # 버튼 상태 복원
            self._display_summary_table() # 요약 표시
            return

        self.log(f"총 {len(self.test_queue)}개 API ({total_variants_to_run} Variants) 테스트 시작...")
        # 첫 번째 테스트 실행 (QTimer 사용)
        QTimer.singleShot(100, self.run_next_test_from_queue)  

    def run_next_test_from_queue(self):
        """ 테스트 큐에서 다음 항목을 가져와 실행합니다. """
        if not self.is_running_all: # 중단된 경우
                # 버튼 상태 복원은 process_api_id_results 또는 run_all_tests 중단 시 처리됨
                return

        if not self.test_queue: # 큐가 비었으면 종료
            self.log("--- ✅ 모든 테스트 완료 ---")
            self.is_running_all = False # 플래그 리셋
            self.run_all_btn.setText("▶ 모든 조회 테스트 실행 (주문 제외)")
            self.update_ui_after_init() # 버튼 상태 복원
            self._display_summary_table() # 최종 요약 표시
            return

        # 큐에서 다음 테스트 가져오기
        base_api_id, test_name, variants, api_id_with_suffix = self.test_queue.pop(0)

        # Worker 실행
        self.log(f"  -> 다음 테스트: '{api_id_with_suffix}: {test_name}' ({len(variants)} Variants)...")
        self.current_test_api_id = api_id_with_suffix # 현재 실행 ID 설정
        # 버튼 스타일 변경 (선택적)
        btn = self.api_buttons.get(api_id_with_suffix)
        if btn: btn.setStyleSheet("background-color: lightblue;") # 실행 중 표시

        self.run_single_test(base_api_id, test_name, variants, api_id_with_suffix)
        # Worker 완료 후 process_api_id_results 에서 다시 run_next_test_from_queue 호출   

    def _display_summary_table(self):
        """ 테스트 결과를 요약하여 로그 창에 테이블 형태로 표시합니다. """
        if not hasattr(self, 'test_results') or not self.test_results:
            self.log("표시할 테스트 결과가 없습니다.", "WARNING")
            return

        summary = "\n\n" + "="*100 + "\n📊 테스트 결과 요약표 (API Variant 기준)\n" + "="*100 + "\n"
        # 헤더 정의 (가변 길이 고려)
        header = f"{'API ID':<22} | {'Var':<6} | {'테스트명':<25} | {'결과':<20} | {'상세 내용'}\n"
        summary += header
        summary += "-" * len(header.split('\n')[0]) + "\n" # 헤더 길이에 맞춰 구분선

        # 통계 집계용 변수
        stats = {"success": 0, "no_data": 0, "api_error": 0, "path_error": 0, "exception": 0, "prepare_error": 0, "skipped": 0, "total_variants": 0}

        # 결과 정렬 (API ID, Variant 순)
        sorted_results = sorted(self.test_results, key=lambda x: (x.get('api_id', ''), x.get('variant_idx', 0)))

        for res in sorted_results:
            api_id = res.get('api_id', 'N/A')
            test_name = res.get('name', 'N/A')[:25] # 이름 길이 제한
            status_code = res.get('status', '❓')
            reason = res.get('reason', 'N/A')
            v_idx = res.get('variant_idx', 0)
            v_tot = res.get('total_variants', 0)
            variant_str = f"{v_idx}/{v_tot}" if v_tot > 0 else "-"

            # 결과 코드 매핑 (통계용)
            status_key = "unknown"
            if status_code == '✅ 성공 (데이터 확인)': status_key = "success"
            elif status_code == '⚠️ 성공 (데이터 없음)': status_key = "no_data"
            elif status_code == '❌ 실패 (API 오류)': status_key = "api_error"
            elif status_code == '❌ 실패 (경로 오류)': status_key = "path_error"
            elif status_code == '❌ 실패 (내부 예외)': status_key = "exception"
            elif status_code == '❌ 실패 (준비 오류)': status_key = "prepare_error"
            elif status_code == '⚪ 건너뜀': status_key = "skipped"

            if status_key != "unknown":
                stats[status_key] += 1
            if v_tot > 0: # 실제 실행된 Variant만 카운트
                stats["total_variants"] += 1

            # 상세 내용 길이 제한
            display_reason = (reason[:40] + '...') if len(reason) > 43 else reason
            # 테이블 라인 추가
            summary += f"{api_id:<22} | {variant_str:<6} | {test_name:<25} | {status_code:<20} | {display_reason}\n"

        # 최종 통계 요약
        total_executed = stats["success"] + stats["no_data"] + stats["api_error"] + stats["path_error"] + stats["exception"]
        total_failed = stats["api_error"] + stats["path_error"] + stats["exception"] + stats["prepare_error"]
        summary += "-" * len(header.split('\n')[0]) + "\n"
        summary += f"총 {len(sorted_results)}개 결과 레코드 (Variant 기준):\n"
        summary += f"  - ✅ 성공 (데이터 확인): {stats['success']}\n"
        summary += f"  - ⚠️ 성공 (데이터 없음): {stats['no_data']}\n"
        summary += f"  - ❌ 실패 합계: {total_failed}\n"
        summary += f"      ㄴ API 오류: {stats['api_error']}, 경로 오류: {stats['path_error']}, 내부 예외: {stats['exception']}, 준비 오류: {stats['prepare_error']}\n"
        summary += f"  - ⚪ 건너뜀 (주문/WS/실시간/빈 정의 등): {stats['skipped']}\n"
        summary += f"(실제 API 호출 시도된 Variant 수: {total_executed})\n"
        summary += "="*100

        self.log(summary, level="INFO") # 결과 테이블 로깅

        # 완료 팝업 메시지 (선택적)
        if total_failed > 0:
            QMessageBox.warning(self, "테스트 완료 (실패 있음)", f"총 {total_executed}개 Variant 시도 중 {total_failed}개 실패.\n상세 내용은 로그를 확인하세요.")
        elif stats["success"] > 0:
            QMessageBox.information(self, "테스트 완료", f"총 {total_executed}개 Variant 시도 완료.\n({stats['success']}개 성공, {stats['no_data']}개 데이터 없음)")
        else:
             QMessageBox.information(self, "테스트 완료", f"총 {total_executed}개 Variant 시도 완료.\n(성공(데이터 확인) 없음)")

    def update_ui_after_init(self):
        """ API 클라이언트 초기화 상태에 따라 UI 요소(라벨, 버튼)를 업데이트합니다. """
        is_ready = self.client_init_success and self.api_client is not None
        status_msg = "" # 메시지 초기화
        color = "gray" # 기본 색상
        account_num = config.ACCOUNT_NUMBER or "설정 필요" # 계좌번호 기본값

        if is_ready:
            token_expiry_str = getattr(self.api_client, 'token_expiry', None)
            expiry_display = f"(토큰 만료: {token_expiry_str.strftime('%Y-%m-%d %H:%M:%S')})" if token_expiry_str else "(토큰 정보 없음)"
            status_msg = f"✅ API 클라이언트 준비 완료 {expiry_display}"; color = "green"
            account_num = getattr(self.api_client, 'account_number', account_num) # 실제 클라이언트 값 사용
            # 입력 위젯 계좌번호 업데이트 (존재하면)
            if hasattr(self, 'account_label'): self.account_label.setText(account_num) # 라벨 직접 업데이트 대신 account_label 사용 (존재 가정)

        else:
            status_msg = self.api_status_label.text() if "❌" in self.api_status_label.text() else "❌ API 클라이언트 초기화 실패"; color = "red"
            # 입력 위젯 계좌번호 업데이트 (존재하면)
            if hasattr(self, 'account_label'): self.account_label.setText(f"{account_num} (연결 실패)") # 라벨 직접 업데이트 대신 account_label 사용 (존재 가정)

        # 상태 라벨 업데이트
        self.api_status_label.setText(status_msg)
        self.api_status_label.setStyleSheet(f"padding: 5px; border: 1px solid {color}; color: {color}; background-color: #f0f0f0;")

        # 모든 *개별* API 버튼 상태 업데이트
        for btn in self.api_buttons.values():
            btn.setEnabled(is_ready)

        # --- [수정] "모든 테스트 실행" 버튼 상태 업데이트 ---
        if hasattr(self, 'run_all_btn'): # 버튼이 생성되었는지 확인 후 업데이트
            self.run_all_btn.setEnabled(is_ready) # <-- 이 줄 추가!

    def _get_common_params(self) -> Dict[str, str]:
        """ UI 입력 위젯에서 값을 읽어 공통 파라미터 딕셔너리를 생성합니다. """
        params = account.p_common.copy() # account.py 기본값 복사
        # 기본 입력 필드
        params["stk_cd"] = self.code_input.text().strip()
        params["ord_qty"] = self.qty_input.text().strip()
        params["ord_uv"] = self.price_input.text().strip() or "0" # 빈칸이면 시장가(0) 가정
        params["orig_ord_no"] = self.orig_ord_no_input.text().strip() or account.p_common.get("dummy_order_id","0000000")
        # 날짜 입력 필드 (YYYYMMDD 형식)
        params["start_dt"] = self.start_date_input.date().toString("yyyyMMdd")
        params["end_dt"] = self.end_date_input.date().toString("yyyyMMdd")
        params["today_str"] = datetime.date.today().strftime("%Y%m%d") # 오늘 날짜 갱신
        params["base_dt"] = params["end_dt"] # base_dt는 보통 종료일 사용
        # account.py p_common 에 필요한 날짜 키가 없으면 현재 날짜 기준으로 계산해서 추가
        if 'one_day_ago_str' not in params: params['one_day_ago_str'] = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        # 추가 코드 입력 필드
        params["etf_cd"] = self.etf_code_input.text().strip()
        params["elw_cd"] = self.elw_code_input.text().strip()
        params["gold_stk_cd"] = self.gold_code_input.text().strip()
        params["cond_seq"] = self.cond_seq_input.text().strip()
        params["inds_cd"] = self.inds_code_input.text().strip()
        params["thema_cd"] = self.thema_code_input.text().strip()

        # 기타 입력 필드 (필요시 추가)
        # if hasattr(self, 'market_input'): params["mrkt_tp"] = self.market_input.text().strip()
        # if hasattr(self, 'sort_input'): params["sort_tp"] = self.sort_input.text().strip()

        return params

    def run_single_test_wrapper(self, api_id_with_suffix, test_name, variants_func):
        """ 버튼 클릭 시 호출되는 래퍼 함수 (Worker 실행 준비) """
        if not self.client_init_success or not self.api_client:
            self.log("API 클라이언트가 준비되지 않아 테스트를 실행할 수 없습니다.", "ERROR"); return
        # 현재 실행 중인 테스트가 있으면 중복 실행 방지 (선택적)
        # if self.current_test_api_id:
        #     self.log(f"'{self.current_test_api_id}' 테스트가 이미 실행 중입니다.", "WARNING"); return

        self.current_test_api_id = api_id_with_suffix # 현재 테스트 ID 설정
        common_params = self._get_common_params() # 현재 입력값 가져오기
        variants = None; base_api_id = api_id_with_suffix.split('_')[0]
        reason = ""; skip_log = False

        try:
            # 1. Variant 생성 시도
            if variants_func: # 버튼에 특정 variant 함수가 지정된 경우
                variants = variants_func(common_params)
            else: # account.py 기본 정의 사용
                 func = account.get_api_definition(base_api_id)
                 if func: variants = func(common_params)
                 # func 자체가 None 이거나 실행 결과가 None인 경우 처리
                 if func is None: raise ValueError(f"'{base_api_id}' 정의 없음")
                 if variants is None: raise ValueError(f"'{base_api_id}' Variants 생성 실패 (함수 None 반환)")

            # 2. 생성 결과 확인
            if variants is None: # 위에서 처리되었지만 안전장치
                 reason = f"'{base_api_id}' 정의 없음 또는 생성 실패"
            elif not isinstance(variants, list):
                 reason = "Variants 결과가 리스트가 아님"
            elif not variants: # 빈 리스트 [] -> 건너뛰기 처리
                 reason = "account.py 정의 비어있음 (실시간/WS API 등)"; skip_log = True
                 # WebSocket API 명시적 확인
                 if base_api_id in ["ka10171", "ka10172", "ka10173", "ka10174"]: reason = "WebSocket 전용 API"
                 # 실시간 등록 ID 확인 (예시)
                 elif base_api_id in ["00","04","0A","0B","0C","0D","0E","0F","0G","0H","OI","OJ","OU","0g","Om","Os","Ou","Ow","1h"]: reason = "실시간 등록 API (테스트 불가)"

        except KeyError as e: reason = f"필수 파라미터 '{e}' 없음"
        except Exception as e: reason = f"Variants 생성 오류: {e.__class__.__name__}: {e}"; self.log(traceback.format_exc(), "DEBUG")

        # 3. 오류 또는 건너뛰기 처리
        if reason:
            if skip_log: status = "⚪ 건너뜀"; level = "INFO"
            else: status = "❌ 실패 (준비)"; level = "ERROR"
            self.log(f"{status} '{api_id_with_suffix}: {test_name}': {reason}.", level)
            # 결과 처리를 위해 process_api_id_results 호출 (오류 상태 전달)
            self.process_api_id_results([("prepare_error", (None, None, reason, None), (None, None), 0)], api_id_with_suffix, test_name, 0)
            self.current_test_api_id = None # 테스트 완료 처리
            return

        # 4. 주문 API 경고
        order_api_ids = ["kt10000", "kt10001", "kt10002", "kt10003", "kt10006", "kt10007", "kt10008", "kt10009", "kt50000", "kt50001", "kt50002", "kt50003"]
        if base_api_id in order_api_ids:
            # 첫 번째 variant 기준으로 정보 표시 (간략화)
            first_variant_body = variants[0][1] if variants else {}
            stk_cd_preview = first_variant_body.get('stk_cd', common_params.get('stk_cd','?'))
            qty_preview = first_variant_body.get('ord_qty', common_params.get('ord_qty','?'))
            price_preview = first_variant_body.get('ord_uv', first_variant_body.get('mdfy_uv', '시장가/미정')) or "시장가"
            action_map = {"kt10000":"매수", "kt10001":"매도", "kt10002":"정정", "kt10003":"취소", "kt10006":"신용매수", "kt10007":"신용매도", "kt10008":"신용정정", "kt10009":"신용취소", "kt50000":"금매수", "kt50001":"금매도", "kt50002":"금정정", "kt50003":"금취소"}
            action = action_map.get(base_api_id, "주문")

            reply = QMessageBox.warning(self, "🚨 실제 주문 경고 🚨",
                                        f"<b>'{test_name}' ({api_id_with_suffix})</b> 테스트는 실제 {action} 요청을 전송합니다.\n"
                                        f"(종목: {stk_cd_preview}, 수량: {qty_preview}, 가격: {price_preview})\n\n"
                                        f"<b>모의투자 계좌인지 반드시 확인하십시오.</b>\n\n계속하시겠습니까?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                self.log(f"ℹ️ '{api_id_with_suffix}: {test_name}' 주문 테스트 취소됨.", "WARNING")
                self.current_test_api_id = None # 테스트 완료 처리
                return

        # 5. Worker 실행
        self.log(f"▶ '{api_id_with_suffix}: {test_name}' 테스트 실행 ({len(variants)} Variants)...", level="INFO")
        # 버튼 비활성화 (선택적)
        # for btn in self.api_buttons.values(): btn.setEnabled(False)
        self.api_buttons.get(api_id_with_suffix).setStyleSheet("background-color: lightgray;") # 현재 버튼만 비활성화 느낌

        self.run_single_test(base_api_id, test_name, variants, api_id_with_suffix)

    def run_single_test(self, api_id_base, test_name, variants: List[Tuple[str, Dict[str, Any]]], api_id_with_suffix: str):
        """ Worker 스레드를 생성하고 시작합니다. """
        if not self.api_client or not hasattr(self.api_client, 'request') or not callable(self.api_client.request):
            msg = f"API 클라이언트({type(self.api_client)})에 호출 가능한 'request' 메서드 없음."; self.log(msg, "CRITICAL")
            self.process_api_id_results([("exception", (None, None, msg, None), (None, None), 0)], api_id_with_suffix, test_name, 0); return

        worker = Worker(self.api_client.request, api_id_base, api_id_with_suffix, test_name, variants)
        worker.signals.api_id_finished.connect(self.process_api_id_results) # 결과 처리 슬롯 연결
        self.threadpool.start(worker) # 스레드풀에서 실행
        QApplication.processEvents() # UI 이벤트 처리

    @pyqtSlot(list, str, str, int)
    def process_api_id_results(self, all_results, api_id_with_suffix, test_name, total_variants):
        """ Worker 스레드 완료 시 호출되는 슬롯 (결과 로깅 및 UI 업데이트) """
        # self.log(f"⏹️ '{api_id_with_suffix}: {test_name}' 테스트 완료 처리 시작...") # 너무 빈번하게 나올 수 있어 주석 처리

        if not hasattr(self, 'test_results'): self.test_results = []

        if not all_results: # 준비 단계에서 오류 발생하여 빈 리스트가 온 경우
             self.log(f"⚪ '{api_id_with_suffix}: {test_name}' 테스트 결과 없음 (준비 실패 또는 Variant 0개).", "WARNING")
             # 결과 리스트에 준비 실패 기록 추가 (요약 테이블용)
             self.test_results.append({
                 "api_id": api_id_with_suffix, "variant_idx": 0, "total_variants": 0,
                 "name": test_name, "status": "❌ 실패 (준비)",
                 "reason": "Variant 생성 실패 또는 정의 없음", "details": None
             })
        else:
            base_api_id = api_id_with_suffix.split('_')[0]
            # is_ranking_api = base_api_id in RANKING_API_IDS # 필요시 사용

            for (result_status, result_data, variant_tuple, variant_idx) in all_results:
                path, body = variant_tuple if variant_tuple else (None, None)
                variant_tag = f"Var {variant_idx}/{total_variants}" if total_variants > 0 else "-"
                data_received = False
                status = '❓ 알 수 없음'; reason = "알 수 없는 결과 상태"; log_level = "ERROR"
                data_for_snippet = None; api_rc = None; api_rm = None

                # --- 결과 상태 분석 ---
                if result_status == "success":
                    data = result_data; api_rc = data.get('return_code'); api_rm = data.get('return_msg', '')
                    list_keys = [k for k, v in data.items() if isinstance(v, list) and k not in ['return_code', 'return_msg']]
                    single_keys = [k for k, v in data.items() if not isinstance(v, list) and k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
                    empty_vals = [None, "", "0", "0.00", "0.0", 0, 0.0, "000000000000000", "N/A", [], {}]
                    has_list = any(len(data.get(k, [])) > 0 for k in list_keys)
                    has_single = any((v_strip := (v.strip() if isinstance(v, str) else v)) not in empty_vals for k in single_keys if (v := data.get(k)) is not None)
                    if has_list or has_single:
                         status = '✅ 성공 (데이터 확인)'; reason = f"성공 (Path: {path or 'N/A'})"; data_received = True; log_level = "INFO"
                    else:
                         status = '⚠️ 성공 (데이터 없음)'; log_level = "WARNING" # 상태 변경
                         no_data_msgs = ["조회 결과가 없습니다", "조회된 내역이 없습니다", "데이터가 없습니다", "해당 내역이 없습니다"]
                         reason = f"정상 (Code 0), 데이터 없음 ({'API 메시지: ' + api_rm if any(m in api_rm for m in no_data_msgs) else '유의미 데이터 없음'})"
                         reason += f" (Path: {path or 'N/A'})"
                    data_for_snippet = data
                elif result_status in ["no_data", "api_error"] and isinstance(result_data, dict):
                     data = result_data; api_rc = data.get('return_code'); api_rm = data.get('return_msg', '오류 메시지 없음')
                     reason = f"{api_rm} (Code: {api_rc}) (Path: {path or 'N/A'})"
                     if api_rc == 20 or "데이터가 없습니다" in api_rm or "조회된 내역이 없습니다" in api_rm: status = '⚠️ 성공 (데이터 없음)'; log_level = "WARNING" # 상태 변경
                     else: status = '❌ 실패 (API 오류)'; log_level = "ERROR"
                     data_for_snippet = api_rm # 오류 메시지 스니펫
                elif result_status in ["path_error", "exception", "prepare_error"] and isinstance(result_data, tuple):
                     _, _, error_msg, _ = result_data # path, body, msg, tb
                     reason = f"{error_msg} (Path: {path or 'N/A'})"
                     if result_status == "path_error": status = '❌ 실패 (경로 오류)'
                     elif result_status == "exception": status = '❌ 실패 (내부 예외)'
                     else: status = '❌ 실패 (준비 오류)' # prepare_error (이론상 여기로 오지 않음)
                     log_level = "CRITICAL" if result_status in ["exception", "prepare_error"] else "ERROR"
                     data_for_snippet = error_msg
                else: # 예상치 못한 경우
                    status = '❓ 알 수 없음'; reason = f"처리 불가 결과: status={result_status}, type={type(result_data)}"; log_level="CRITICAL"
                    data_for_snippet = str(result_data)

                # --- 결과 로깅 ---
                log_msg = f"{status} [{api_id_with_suffix} {variant_tag}] {test_name:<25} | {reason}"; self.log(log_msg, level=log_level)

                # --- 데이터 스니펫 표시 ---
                if data_received and isinstance(data_for_snippet, dict):
                     try:
                         snippet = self._format_data_snippet(data_for_snippet, base_api_id)
                         if self.show_details_checkbox.isChecked(): # 상세 보기 옵션
                             try: full_pretty = json.dumps(data_for_snippet, indent=2, ensure_ascii=False)
                             except: full_pretty = str(data_for_snippet)
                             self.log(f"--- 상세 데이터 ({api_id_with_suffix} {variant_tag}) ---\n{full_pretty}\n-------------------------", level="DEBUG")
                         elif snippet: # 스니펫이 있으면 출력
                             self.log(snippet.strip(), level="INFO")
                         # else: # 스니펫 생성 실패 시 (이미 로그 남김)
                     except Exception as e: self.log(f"[{api_id_with_suffix} {variant_tag}] 스니펫 생성/로깅 오류: {e}", level="WARNING")

                # --- 결과 저장 (요약 테이블용) ---
                self.test_results.append({
                    "api_id": api_id_with_suffix, "variant_idx": variant_idx, "total_variants": total_variants,
                    "name": test_name, "status": status,
                    "reason": reason if isinstance(reason, str) else str(result_data), # 문자열로 변환
                    "details": (path, body, result_data) # path, body, result_data (dict or tuple)
                })

        # --- 테스트 완료 후 처리 ---
        # 현재 테스트 버튼 스타일 복원
        btn = self.api_buttons.get(api_id_with_suffix)
        if btn: btn.setStyleSheet("") # 배경색 복원
        self.current_test_api_id = None # 현재 테스트 ID 초기화

        # "모든 테스트 실행" 중이었으면 다음 테스트 호출
        if hasattr(self, 'is_running_all') and self.is_running_all:
            QTimer.singleShot(50, self.run_next_test_from_queue) # 짧은 지연 후 다음 호출
        else: # 개별 테스트 완료 시 (API 클라이언트 상태에 따라 버튼 활성화)
             if self.client_init_success:
                 self.update_ui_after_init() # 버튼 상태 업데이트

    def _format_data_snippet(self, data: Dict, base_api_id: str) -> str:
        """ API 응답 데이터의 요약 문자열(스니펫)을 생성합니다. """
        snippet = ""
        try:
            list_keys = [k for k, v in data.items() if isinstance(v, list) and k not in ['return_code', 'return_msg']]
            single_keys = [k for k, v in data.items() if not isinstance(v, list) and k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
            empty_vals = [None, "", "0", "0.00", "0.0", 0, 0.0, "000000000000000", "N/A", [], {}]

            if list_keys: # 리스트 데이터가 있는 경우 (주로 output1, list 등)
                key = list_keys[0]; items = data.get(key, [])
                snippet += f"  > 목록 '{key}' ({len(items)}개):"
                # 상위 3개 항목만 표시 (정보량 조절)
                for i, item in enumerate(items[:3]):
                    # 대표적인 키 값 추출 시도 (종목명, 코드, 가격, 수량/값 등)
                    name = item.get('stk_nm', item.get('name', item.get('inds_nm', '')))[:10] # 이름 길이 제한
                    code = item.get('stk_cd', item.get('code', item.get('inds_cd', '')))
                    price = item.get('stk_prpr', item.get('cur_prc', item.get('cntr_pric', item.get('clpr', '')))) # 현재가, 체결가, 종가 등
                    value = item.get('trde_qty', item.get('acml_vol', item.get('ord_qty', item.get('evlt_amt', '')))) # 거래량, 누적거래량, 주문수량, 평가금액 등
                    line = f"    {i+1}."
                    if code: line += f" [{code.strip()}]"
                    if name: line += f" {name.strip()}"
                    if price: line += f" (가격:{price.strip()})"
                    if value: line += f" (값:{value.strip()})"
                    snippet += "\n" + line.strip()
                if len(items) > 3: snippet += "\n    ..."
            elif single_keys: # 단일 값들만 있는 경우
                 snippet += "  > 주요 값:"
                 count = 0
                 for k in single_keys:
                     v = data.get(k)
                     # 비어있지 않은 값 상위 5개 표시
                     if (v_strip := (str(v).strip() if v is not None else "")) and v_strip not in empty_vals:
                          snippet += f"\n    - {k}: {v_strip}"
                          count += 1
                          if count >= 5: break
                 if count == 0: # 보여줄 값이 없으면 처음 3개 키라도 표시
                      for k in single_keys[:3]: snippet += f"\n    - {k}: {data.get(k)}"
            else: # 리스트도 단일값도 없는 경우 (return_code, return_msg 만 있는 경우)
                 snippet = "  > 데이터 필드 없음."

        except Exception as e:
            snippet = f"  > 스니펫 생성 오류: {e}"
            # [수정] self.logger 사용
            self.logger.warning(f"데이터 스니펫 생성 중 오류 ({base_api_id}): {e}") #

        return snippet

    # --- PyQt 이벤트 핸들러 ---
    def closeEvent(self, event):
        """ 창 닫기 이벤트 처리 (스레드 정리) """
        self.log("디버거 창 닫기 요청됨. 스레드 정리 중...")
        self.threadpool.clear() # 큐에 있는 작업 취소
        self.threadpool.waitForDone(3000) # 최대 3초 대기
        self.log("스레드 정리 완료. 종료합니다.")
        event.accept()

# --- 메인 실행 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ComprehensiveDebuggerWindow()
    window.show()
    sys.exit(app.exec_())