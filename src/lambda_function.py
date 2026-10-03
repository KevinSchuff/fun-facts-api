"""Kleine Fun-Fact Website"""

import json
import random
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path


FACTS = tuple(
    {"id": index, "text": text}
    for index, text in enumerate(
        json.loads(Path(__file__).with_name("facts.json").read_text(encoding="utf-8")),
        start=1,
    )
)


def fact_of_the_day(day=None):
    """Ein Fact pro Kalendertag (UTC); der 29. Februar nutzt den 28. Februar."""
    if day is None:
        day = datetime.now(timezone.utc).date()
    if day.month == 2 and day.day == 29:
        day = day.replace(day=28)
    # Ein festes Nicht-Schaltjahr hält die Zuordnung für Monat und Tag stabil.
    calendar_day = day.replace(year=2001)
    index = (calendar_day - date(2001, 1, 1)).days
    return FACTS[index]


def make_home_response():
    """Startseite aktuellen Tages-Fact."""
    text = escape(fact_of_the_day()["text"])
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store",
        },
        "body": f"""<!doctype html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Fun Fact of the Day</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; min-height: 100svh; padding: 1.5rem;
                display: grid; place-items: center;
                font-family: system-ui, sans-serif;
                background: #f1f5f9; color: #1e293b; }}
        main {{ width: 100%; max-width: 40rem;
                padding: clamp(1.5rem, 5vw, 3rem);
                background: #fff; border: 1px solid #e2e8f0;
                border-top: 4px solid #6366f1; border-radius: 1rem;
                box-shadow: 0 12px 36px rgb(15 23 42 / 6%); }}
        h1 {{ margin: 0 0 1.25rem; font-size: 1.25rem; color: #4f46e5; }}
        p {{ margin: 0; font-size: clamp(1.2rem, 3vw, 1.5rem);
             line-height: 1.7; overflow-wrap: anywhere; }}
    </style>
</head>
<body>
    <main>
        <h1>Fun Fact of the Day:</h1>
        <p>{text}</p>
    </main>
</body>
</html>""",
        "isBase64Encoded": False,
    }


def make_response(status_code, data, extra_headers=None):
    """Verpackt facts in http für Lambda."""
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if extra_headers:
        headers.update(extra_headers)
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(data, ensure_ascii=False),
        "isBase64Encoded": False,
    }


def handle_request(method, path):
    """Enthält die API Logik."""
    if method != "GET":
        return make_response(
            405,
            {"error": "Nur GET-Anfragen sind erlaubt."},
            {"Allow": "GET"},
        )

    if path == "/":
        return make_home_response()
    if path == "/fact":
        return make_response(200, random.choice(FACTS))
    if path == "/facts":
        return make_response(200, {"facts": FACTS, "count": len(FACTS)})

    return make_response(404, {"error": "Dieser Pfad existiert nicht."})


def lambda_handler(event, context):
    """AWS ruft diesen Einstiegspunkt mit den Daten der HTTP-Anfrage auf."""
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "")
    path = event.get("rawPath", "/")
    return handle_request(method, path)
