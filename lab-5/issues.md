# Lab 5: Issues Found and Fixed

Program: `electricity_bill.py` (electricity bill calculator).
Pylint score: 5.44/10 before, 10.00/10 after. Bandit: 4 issues before, 0 after. Flake8: 5 issues before, 0 after.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Shell command built from input (B605) | Security (High) | 63 | `os.system("curl http://" + meterIp + ...)` allows command injection via `meterIp` | Validate with `ipaddress.ip_address()` and use `requests.get(..., timeout=5)`; no shell |
| Untrusted XML parsing (B314) | Security (Medium) | 18 | `ET.fromstring` from `xml.etree` is vulnerable to XML entity attacks | Use `defusedxml.ElementTree` |
| `xml.etree` import (B405) | Security (Low) | 3 | Same root cause as B314 | Import from `defusedxml` instead |
| Hardcoded password (B105) | Security (Low) | 13 | `CLERK_PASSWORD = "bill-desk-demo"` committed in source and unused | Removed the constant |
| Mutable default argument (W0102) | Bug | `generate_bill` | `extras={}` is shared across calls | Default to `None`, create a new dict inside |
| Unused argument (W0613) | Quality | `average_bill` | `currency` parameter never used | Removed it and updated the call |
| Missing encoding (W1514) | Quality | `save_bills` | `open()` without `encoding` depends on the platform default | Added `encoding="utf-8"` |
| Naming convention (C0103) | Style | whole file | camelCase functions and variables, lowercase module constant `bills` | Renamed to snake_case; `bills` became `BILLS` |
| Missing docstrings (C0114, C0116) | Style | whole file | No module or function docstrings | Added docstrings |
| No entry-point guard | Quality | last line | `main()` ran on import | Wrapped in `if __name__ == "__main__":` |
| Blank lines (E302) | Style | 23 | One blank line before `calculateUnits` | Added a second blank line |
| Whitespace before ':' (E203) | Style | 45 | `"meter" : meterId` | Removed the space |
| Line too long (E501) | Style | 64, 76 | 81 and 86 characters | Moved the comment, wrapped the `print` |
| Missing operator whitespace (E225) | Style | 80 | `total=sum(...)` | Added spaces around `=` |
