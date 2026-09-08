"""Entry point for the double-click Windows app.

Gets the IFRA Standards list, saves it to the Desktop as a CSV, and prints
plain-language progress. Any error is shown in full and the window stays open
so the message can be read or copied. This module is what the packaged .exe
runs; it deliberately keeps its output friendly rather than terse.
"""

from __future__ import annotations

import sys
import traceback
from datetime import date
from pathlib import Path


def _desktop() -> Path:
    """Best guess at the user's Desktop, allowing for OneDrive redirection."""
    home = Path.home()
    candidates = [home / "Desktop", home / "OneDrive" / "Desktop"]
    candidates += sorted(home.glob("OneDrive*/Desktop"))
    for path in candidates:
        if path.is_dir():
            return path
    return home


def main() -> int:
    # Used by the build to confirm the packaged .exe starts and imports cleanly,
    # without going online.
    if "--check" in sys.argv[1:]:
        import ifra_standards

        print(f"ifra-standards app {ifra_standards.__version__} ok")
        return 0

    print("IFRA Standards spreadsheet maker")
    print("===============================")
    print()
    try:
        from ifra_standards import fetch_standards, write

        print("Step 1 of 2: getting the current list from ifrafragrance.org")
        standards = fetch_standards()
        print(f"            got {len(standards)} standards")

        out = _desktop() / f"IFRA Standards {date.today():%Y-%m-%d}.csv"
        print()
        print("Step 2 of 2: saving the spreadsheet")
        write(standards, out)
        print(f"            saved to: {out}")
        print()
        print("Done. Open that file in Excel.")
        code = 0
    except Exception:
        print()
        print("Something went wrong. The details are below. You can copy this")
        print("and paste it into a new issue at:")
        print("  https://github.com/maurwhal/ifra-standards/issues")
        print()
        traceback.print_exc(file=sys.stdout)
        code = 1

    print()
    try:
        input("Press Enter to close this window. ")
    except EOFError:
        pass
    return code


if __name__ == "__main__":
    sys.exit(main())
