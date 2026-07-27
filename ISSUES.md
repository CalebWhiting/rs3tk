# Issues

## Known gaps

### Avatar cache endpoint is unimplemented

**Status:** documented, not implemented
**Location:** `src/rs3tk/backend.py:_serve_avatar` (TODO comment)

The `/api/avatar/{name}` endpoint reads from `~/.config/rs3tk/cache/avatar_{name}.png` but nothing ever writes to that path. Every avatar request 404s.

To close: re-introduce `get_player_avatar` in `rs3tk/rs_api.py` (it was removed during the 2025-08 dead-code cleanup) and have `_serve_avatar` (or a new downloader endpoint) call it and write the PNG to the cache before serving.

### `get_news(locale=0)` is indistinguishable from "use default locale"

**Status:** known gotcha, documented in `tests/test_app.py`
**Location:** `src/rs3tk/app.py:get_news`

The expression `locale=locale if locale else settings.locale` treats `locale=0` as "use default". If you need to pass `0` (English) explicitly, there's no way to do so today. Fix options: use a sentinel object, split the parameter (`locale_or_none` plus `force_default`), or change the default to `-1`.

## Tracking

Issues found during the 2025-08 audit + refactor + test-coverage push (branch `gui`).
