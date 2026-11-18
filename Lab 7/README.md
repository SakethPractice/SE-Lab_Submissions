# L6_L7_40 — Ride Share Fare

Lab 7: Fuzz Testing

## About

A small Python module that parses trip details, averages fares and works out the payable fare after a promo.

## Files

| File | Description |
|------|-------------|
| `ride_share_fare.py` | The code under test |
| `test_ride_share_fare.py` | Starter test file |

Refer to the lab handout for instructions.

## Run

From the repository root:

```powershell
python -m pip install hypothesis pytest
Set-Location "Lab 7"
python ride_share_fare.py
python -m pytest test_ride_share_fare.py
```

The application functions return `None` for malformed, unsupported, or
out-of-range inputs. Valid inputs retain their original return formats.
