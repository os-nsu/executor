#!/bin/bash  

TC=/sbin/tc
IP=/sbin/ip
MODPROBE=/sbin/modprobe

INTERFACE="";
UPLOAD_SPEED_LIMIT="";
DOWNLOAD_SPEED_LIMIT="";
LIMIT_APPLY_TO=0.0.0.0;
ACTION="add_rules";
IFB="ifb0";

function remove_rules {
    if [[ -z $INTERFACE ]]; then
        echo "interface name is required";
        exit 1;
    fi

    $TC qdisc del dev $INTERFACE   root 2>/dev/null;
    $TC qdisc del dev $IFB         root 2>/dev/null;
    $TC qdisc del dev $INTERFACE   ingress 2>/dev/null;
    $TC qdisc del dev $IFB         ingress 2>/dev/null;
}

function add_rules {
    if [[ -z $INTERFACE ]]; then
        echo "interface name is required";
        exit 1;
    fi

    if [[ -z $DOWNLOAD_SPEED_LIMIT ]]; then
        echo "download speed limit is required";
        exit 1;
    fi

    if [[ -z $UPLOAD_SPEED_LIMIT ]]; then
        echo "upload speed limit is required";
        exit 1;
    fi

    remove_rules;

    $TC qdisc add dev $INTERFACE root handle 1: htb default 20;
    $TC class add dev $INTERFACE parent 1: classid 1:1 htb rate "${UPLOAD_SPEED_LIMIT}kbit" prio 5;

    RATE=$((50*${UPLOAD_SPEED_LIMIT}/100))
    if [ "$RATE" -eq 0 ]; then
        RATE=1;
    fi

    $TC class add dev $INTERFACE parent 1:1 classid 1:10 htb \
        rate "${RATE}kbit" ceil "${UPLOAD_SPEED_LIMIT}kbit" prio 1;

    RATE=$((50*${UPLOAD_SPEED_LIMIT}/100))
    if [ "$RATE" -eq 0 ]; then
        RATE=1;
    fi

    $TC class add dev $INTERFACE parent 1:1 classid 1:20 htb \
        rate "${RATE}kbit" ceil "${UPLOAD_SPEED_LIMIT}kbit" prio 2;

    $MODPROBE ifb numifbs=1;
    $IP link set dev $IFB up;

    $TC qdisc add dev $INTERFACE handle ffff: ingress;
    $TC filter add dev $INTERFACE parent ffff: protocol ip u32 match u32 0 0 \
        action mirred egress redirect dev $IFB;

    $TC qdisc add dev $IFB root handle 2: htb;
    $TC class add dev $IFB parent 2: classid 2:1 htb rate "${DOWNLOAD_SPEED_LIMIT}kbit";

    $TC filter add dev $IFB protocol ip parent 2: prio 1 u32 match ip src $LIMIT_APPLY_TO/0 flowid 2:1;
}

function check_rules {
    $TC -s qdisc ls dev $INTERFACE;
}

function print_usage {
    echo "$0 [-hc] [-a <adapter>] [-d <rate>] [-u <rate>]";
    echo -e "-h  help";
    echo -e "-c  remote rules";
    echo -e "-a  interface name";
    echo -e "-d  download speed rate";
    echo -e "-u  upload speed rate";
}

if [ $# -eq 0 ]; then
    print_usage;
    exit 1;
fi

while getopts ":hca:u:d:" opt; do
    case $opt in
        h)
            ACTION="print_usage"
            ;;
        c)
            ACTION="remove_rules"
            ;;
        a)
            INTERFACE="$OPTARG"
            ;;
        d)
            DOWNLOAD_SPEED_LIMIT="$OPTARG"
            ;;
        u)
            UPLOAD_SPEED_LIMIT="$OPTARG"
            ;;
        :)
            echo "Option -$OPTARG argument required." >&2
            exit 1
            ;;
        ?)
            echo "incorrect param: -$OPTARG" >&2
            exit 1
            ;;
    esac
done


if [ "$ACTION" == "add_rules" ]; then
    add_rules;
elif [ "$ACTION" == "remove_rules" ]; then
    remove_rules;
else
    print_usage;
fi
