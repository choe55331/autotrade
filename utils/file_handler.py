"""
utils/file_handler.py
파일 입출력 처리
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FileHandler:
    """
    파일 입출력 핸들러
    
    주요 기능:
    - JSON 파일 읽기/쓰기
    - 파일 존재 확인
    - 백업 파일 생성
    """
    
    @staticmethod
    def read_json(file_path: Path) -> Optional[Dict[str, Any]]:
        """
        JSON 파일 읽기
        
        Args:
            file_path: 파일 경로
        
        Returns:
            JSON 데이터 (실패 시 None)
        """
        try:
            if not file_path.exists():
                logger.warning(f"파일이 존재하지 않습니다: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"JSON 파일 읽기 성공: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {file_path} - {e}")
            return None
        except Exception as e:
            logger.error(f"파일 읽기 오류: {file_path} - {e}")
            return None
    
    @staticmethod
    def write_json(
        file_path: Path,
        data: Dict[str, Any],
        indent: int = 2,
        backup: bool = False
    ) -> bool:
        JSON 파일 쓰기
        
        Args:
            file_path: 파일 경로
            data: 저장할 데이터
            indent: 들여쓰기
            backup: 백업 파일 생성 여부
        
        Returns:
            성공 여부
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if backup and file_path.exists():
                FileHandler._create_backup(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.debug(f"JSON 파일 쓰기 성공: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"파일 쓰기 오류: {file_path} - {e}")
            return False
    
    @staticmethod
    def _create_backup(file_path: Path):
        """
        백업 파일 생성
        
        Args:
            file_path: 원본 파일 경로
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = file_path.with_suffix(f'.{timestamp}.bak')
            
            import shutil
            shutil.copy2(file_path, backup_path)
            
            logger.debug(f"백업 파일 생성: {backup_path}")
            
        except Exception as e:
            logger.warning(f"백업 파일 생성 실패: {e}")
    
    @staticmethod
    def exists(file_path: Path) -> bool:
        """
        파일 존재 확인
        
        Args:
            file_path: 파일 경로
        
        Returns:
            존재 여부
        """
        return file_path.exists()
    
    @staticmethod
    def create_directory(dir_path: Path):
        """
        디렉토리 생성
        
        Args:
            dir_path: 디렉토리 경로
        """
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"디렉토리 생성: {dir_path}")
        except Exception as e:
            logger.error(f"디렉토리 생성 오류: {dir_path} - {e}")
    
    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """
        파일 삭제
        
        Args:
            file_path: 파일 경로
        
        Returns:
            성공 여부
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"파일 삭제: {file_path}")
                return True
            else:
                logger.warning(f"파일이 존재하지 않습니다: {file_path}")
                return False
        except Exception as e:
            logger.error(f"파일 삭제 오류: {file_path} - {e}")
            return False
    
    @staticmethod
    def read_text(file_path: Path) -> Optional[str]:
        """
        텍스트 파일 읽기
        
        Args:
            file_path: 파일 경로
        
        Returns:
            파일 내용
        """
        try:
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"텍스트 파일 읽기 오류: {file_path} - {e}")
            return None
    
    @staticmethod
    def write_text(file_path: Path, content: str) -> bool:
        """
        텍스트 파일 쓰기
        
        Args:
            file_path: 파일 경로
            content: 내용
        
        Returns:
            성공 여부
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            logger.error(f"텍스트 파일 쓰기 오류: {file_path} - {e}")
            return False


__all__ = ['FileHandler']