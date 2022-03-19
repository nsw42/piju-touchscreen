#! /bin/bash

pytest --cov=apiclient \
       --cov=artworkcache \
       --cov=screenblankmgr \
       --cov-report=xml
