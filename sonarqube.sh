#! /bin/bash

sonar-scanner  \
  -Dsonar.projectKey=pijuui \
  -Dsonar.sources=./src \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.python.version=3.9 \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.login=3377f7f1b54bd9473619970a1d5e1bf81f09187a
