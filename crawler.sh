#!/bin/sh
PATH=/usr/local/bin:/usr/local/sbin:~/bin:/usr/bin:/bin:/usr/sbin:/sbin
python="/usr/local/anaconda3/bin/python3.7"
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi
attempt=0
while :; do

  echo curling...
  $python --version
   ((
	cd /Users/marketit/marketit/reservation_bot && \
  # chmod 755 crawler.py
	$python crawler.py --email '' --password '' --date '2019-08-30 10:00'

	) > /Users/marketit/marketit/reservation_bot/crawler2.log 2>&1)
   echo finish
   sleep 5
   attempt=$((attempt + 1))
   if [ "$attempt" -gt 600 ]; then
    exit 1
   fi
done
