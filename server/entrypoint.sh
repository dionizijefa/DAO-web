#!/bin/sh
conda init bash
conda activate dao_web
uwsgi --ini /etc/uwsgi.ini
