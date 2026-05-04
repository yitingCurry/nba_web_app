# NBA Web

## Run backend + frontend

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start server from `nba_web/backend`:

```bash
uvicorn main:app --reload
```

3. Open browser:

- http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Current status

- `GET /api/player/{player_name}` is implemented.
- Other APIs are stubs for next migration steps.
