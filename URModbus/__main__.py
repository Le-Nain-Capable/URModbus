from pathlib import Path
import sys


# When executed with `python URModbus`, Python does not add the
# directory containing the URModbus package to sys.path.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from URModbus.cli import main


raise SystemExit(main())
