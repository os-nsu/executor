#!/bin/bash  

TC=/sbin/tc

INTERFACE=wlp0s20f3
INTERFACE_SPEED=100mbit
UPLOAD_SPEED_LIMIT=400kbps
DOWNLOAD_SPEED_LIMIT=400kbps
LIMIT_APPLY_TO=0.0.0.0

function remove_rules {
    $TC qdisc del dev $INTERFACE root
}

function add_rules { 
    remove_rules

    $TC qdisc add dev $INTERFACE root handle 1:0 htb default 10
    $TC class add dev $INTERFACE parent 1:0 classid 1:1 htb rate $INTERFACE_SPEED
    $TC class add dev $INTERFACE parent 1:1 classid 1:10 htb rate 5mbit ceil $UPLOAD_SPEED_LIMIT
    $TC class add dev $INTERFACE parent 1:1 classid 1:30 htb rate 5mbit ceil $DOWNLOAD_SPEED_LIMIT

    $TC filter add dev $INTERFACE protocol ip parent 1:0 prio 2 u32 match ip dst $LIMIT_APPLY_TO/32 flowid 1:10
    $TC filter add dev $INTERFACE protocol ip parent 1:0 prio 1 u32 match ip dst $LIMIT_APPLY_TO/32 flowid 1:30
}

function check_rules {
    $TC -s qdisc ls dev $INTERFACE
}

function print_usage {
    echo "USAGE: speed_ctl [OPTION]"
    echo "add_rules - add limit rules for network interface"
    echo "remove_rules - remove rules"
    echo "check_rules - show rules"
}

if [ -z "$1" ]; then
    print_usage
elif [ "$1" == "add_rules" ]; then
    add_rules
elif [ "$1" == "remove_rules" ]; then
    remove_rules
elif [ "$1" == "check_rules" ]; then
    check_rules
fi
