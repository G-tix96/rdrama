#!/bin/bash

cd /rDrama
git pull

. /env
PATH="${NVM_DIR}/versions/node/v${NODE_VERSION}/bin/:${PATH}"

cd ./chat
yarn install
yarn chat
cd ..

gunicorn files.__main__:app load_chat -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:5001 --max-requests 30000 --max-requests-jitter 30000
