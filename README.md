# Fun Facts – Lernprojekt mit AWS Lambda und CI/CD

[![CI/CD](https://github.com/KevinSchuff/fun-facts-api/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/KevinSchuff/fun-facts-api/actions/workflows/ci.yml)


Hauptziel dieses Lernprojekts ist das Kennenlernen von AWS und CI/CD. Als Nebenprodukt ergab sich eine Website mit "Fun" Facts.

Zur Website: [Fun Facts](https://lgzau7dktkt646c3zykl75msgu0nyavd.lambda-url.eu-central-1.on.aws/)

## Aufbau

Die Anwendung läuft auf AWS Lambda mit Python 3.14 und ist über eine HTTPS
Function URL im Browser oder per HTTP-Anfrage erreichbar.

GitHub Actions führt bei Pushes und Pull Requests automatisch die Tests aus.
Nach erfolgreichen Tests bei einem Push auf `main` wird der Code auf AWS Lambda
aktualisiert. Die Anmeldung bei AWS erfolgt über OIDC mit kurzlebigen Zugangsdaten.

## Was ich gelernt habe

- Eine Python-Anwendung über AWS Lambda und eine HTTPS Function URL bereitstellen.
- Vorhandene unittest-Tests in GitHub Actions automatisch ausführen.
- CI und CD unterscheiden und Deployments von erfolgreichen Tests abhängig machen.
- GitHub über OIDC mit AWS verbinden und IAM-Berechtigungen gezielt begrenzen.
