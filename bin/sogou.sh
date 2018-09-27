#!/bin/bash
# author jiaoguofu

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$CURDIR/../src
export CONF=$CURDIR/../conf
export SRC=$CURDIR/../src

supervisor_pid=/root/work/log/supervisord_sogou.pid

start() {
    if [ -f ${supervisor_pid} ]; then
        echo -e "\033[31m==> there are another supervisord process working, try to resart the service\033[0m"
        restart
        exit 1
    fi
    echo "==> starting service..."
    supervisord -c /root/work/supervisord.conf
    sleep 3
    status
}

stop_server() {
    echo "==> stopping service..."
    for pid in `ps aux | grep -v "grep" | grep "main.py" |grep "python3"| awk '{print $2}'`
    do
        if kill -0 $pid > /dev/null 2>&1; then
            kill $pid
        fi
    done
}

stop_supervisord() {
    echo "==> stopping supervisord..."

    su_pid=`cat ${supervisor_pid}`
    if [[ $su_pid ]]; then
        if kill -0 $su_pid > /dev/null 2>&1; then
            kill -9 $su_pid
        fi
    fi
    rm -f ${supervisor_pid}
}

stop() {
    stop_supervisord
    stop_server
}

restart() {
    echo "=> restarting service..."
    stop
    start
}

status() {
    cd $bin/..
    supervisorctl -c /root/work/supervisord.conf status
}

case "$1" in
    start|stop|restart|status)
        $1
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac
