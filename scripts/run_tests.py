"""테스트 실행 스크립트"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """테스트 실행"""
    project_root = Path(__file__).parent.parent
    
    # pytest 실행
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        cwd=project_root,
    )
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())

