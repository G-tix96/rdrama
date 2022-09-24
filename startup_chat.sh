cd /rDrama
git pull
cd ./chat && yarn chat && cd ../
. /env
gunicorn files.__main__:app load_chat -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:5001 --max-requests 30000 --max-requests-jitter 30000