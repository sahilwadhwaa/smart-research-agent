import json


def format_sse(event: str, data: dict[str, str]) -> str:
        """
        Build a single SSE message.

        event: event name (e.g., 'delta', 'done', 'error')
        data:  JSON-serializable dict
        """
        return (
            f"event: {event}\n"
            f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        )