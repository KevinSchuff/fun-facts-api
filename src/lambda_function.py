"""Kleine Fun-Fact-API ohne zusätzliche Python-Pakete."""

import json
import random


FACTS = (
    {"id": 1, "text": "Ein Oktopus hat drei Herzen."},
    {"id": 2, "text": "Die Venus braucht für eine Drehung um ihre Achse länger als für einen Umlauf um die Sonne."},
    {"id": 3, "text": "Ein Würfel hat sechs Flächen, zwölf Kanten und acht Ecken."},
)


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
        return make_response(200, {
            "message": "Willkommen bei der Fun-Fact-API!",
            "endpoints": ["GET /fact", "GET /facts"],
        })
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
