# Lab 5: Issues Found and Fixed

Program: `electricity_bill.py` (electricity bill calculator).
Pylint score: 5.44/10 before, 10.00/10 after. Bandit: 4 issues before, 0 after. Flake8: 4 issues before, 0 after.
Line numbers refer to the original file (see `reports/*_before.txt`).

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Shell command built from input (B605) | Security (High) | 63 | `os.system("curl http://" + meterIp + ...)` allows command injection via `meterIp` | Validate with `ipaddress.ip_address()` and use `requests.get(..., timeout=5)`; no shell |
| Untrusted XML parsing (B314) | Security (Medium) | 18 | `ET.fromstring` from `xml.etree` is vulnerable to XML entity attacks | Use `defusedxml.ElementTree` |
| `xml.etree` import (B405) | Security (Low) | 3 | Same root cause as B314 | Import from `defusedxml` instead |
| Hardcoded password (B105) | Security (Low) | 13 | `CLERK_PASSWORD = "bill-desk-demo"` committed in source and unused | Removed the constant |
| Mutable default argument (W0102) | Bug | 42 | `extras={}` in `generateBill` is shared across calls | Default to `None`, create a new dict inside |
| Unused argument (W0613) | Quality | 50 | `currency` parameter of `averageBill` never used | Removed it and updated the call |
| Missing encoding (W1514) | Quality | 57 | `open()` without `encoding` depends on the platform default | Added `encoding="utf-8"` |
| Naming convention (C0103) | Style | 17-67 | camelCase functions, arguments and variables (`readMeters`, `slabUnits`, `meterId`, ...) | Renamed to snake_case; also renamed module list `bills` to `BILLS` for consistency |
| Missing docstrings (C0114, C0116) | Style | 1, 17, 22, 29, 42, 50, 56, 61, 66 | No module or function docstrings | Added docstrings |
| No entry-point guard | Quality (manual, not tool-reported) | last line | `main()` ran on import | Wrapped in `if __name__ == "__main__":` |
| Blank lines (E302) | Style | 22 | One blank line before `calculateUnits` | Added a second blank line |
| Whitespace before ':' (E203) | Style | 44 | `"meter" : meterId` | Removed the space |
| Line too long (E501) | Style | 72 | `print` line is 86 characters | Wrapped the `print` |
| Missing operator whitespace (E225) | Style | 76 | `total=sum(...)` | Added spaces around `=` |
