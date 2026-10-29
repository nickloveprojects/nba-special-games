import os
import sys
import tempfile
from pathlib import Path

_t = tempfile.mkdtemp()
os.environ["NBA_DATA_DIR"] = _t + "/data"
os.environ["NBA_OUT_DIR"] = _t + "/out"
os.environ["NBA_SLEEP"] = "0"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
