# x402 Weather API

A paid weather API using x402 payments.
Price: $0.0001 USDC per request.

## Deploy to Railway

1. Connect `ryanclawjr-lab/workspace` to Railway
2. Set `PYTHON=python3` in environment
3. Deploy command: `python3 weather-api/server.py`
4. Port: `3000`

## Endpoints

- `/health` - Health check (free)
- `/weather?lat=40.71&lon=-74.00` - Current weather
- `/forecast?lat=40.71&lon=-74.00&days=7` - Forecast
