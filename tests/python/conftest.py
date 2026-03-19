import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parents[2] / 'scripts'
sys.path.insert(0, str(scripts_dir))
