# start.sh
#/root/Downloads/neo4j-community-2.3.1/bin/
#export SPARK_HOME=/home/satheesh/spark-1.6.0-bin-hadoop2.6
#export SPARK_HOME=/home/ec2-user/spark-1.6.0-bin-hadoop2.6/
#export PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH
export APP_CONFIG_FILE=../config/development.py
#export CELERY_CONFIG_FILE=../instance/flaskapp.cfg
#export CELERY_CONFIG_FILE=../config/development.py
export C_FORCE_ROOT=True
#service php-fpm start
#export APP_CONFIG_FILE=../config/production.py
#service rabbitmq-server start
python app.py -l debug
#uwsgi dragon.ini
#celery -A tasks worker -l info --concurrency=10 --autoreload
#flower -A tasks --port=5555
#celery -A tasks purge -f
#flower -A tasks --port=5555
#/home/neo4j-community-2.3.2/bin
#uwsgi dragon.ini --plugin python --logto /tmp/wowgic_flask.log
