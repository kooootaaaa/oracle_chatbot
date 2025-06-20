#!/bin/bash
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH
source /home/kota/oracle_chatbot_env/bin/activate
python manage.py runserver 8001