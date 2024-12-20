#!/bin/bash

IP=/sbin/ip
IPTABLES=/sbin/iptables

ACTION="print_usage";
NS_NAME="";
VETH_NAME="";
VETH_FRONT_IP="";
VETH_BACK_IP="";
BASE_ETH=""

#enable ip forwarding for iptables support
echo 1 > /proc/sys/net/ipv4/ip_forward

function create_veth {
	if [[ -z $NS_NAME ]]; then
		echo "namespace name is required";
		exit 1;
	fi

	if [[ -z $VETH_NAME ]]; then
		echo "veth name is required";
		exit 1;
	fi

	if [[ -z $BASE_ETH ]]; then
		echo "base eth name is required";
		exit 1;
	fi

	if [[ -z $VETH_BACK_IP ]]; then
		echo "veth back-ip name is required";
		exit 1;
	fi

	if [[ -z $VETH_FRONT_IP ]]; then
		echo "veth front-ip name is required";
		exit 1;
	fi

	$IP netns add $NS_NAME;

	#attach loopback adapter
	$IP netns exec $NS_NAME ip link set lo up;

	#create veth
	#veth is created in pairs (just like a real ethernet cable)
	$IP link add $VETH_NAME"a" type veth peer name $VETH_NAME"b";
	$IP link set $VETH_NAME"b" netns $NS_NAME;

	$IP addr add $VETH_FRONT_IP/24 dev $VETH_NAME"a";
	$IP netns exec $NS_NAME ip addr add $VETH_BACK_IP/24 dev $VETH_NAME"b";

	$IP link set $VETH_NAME"a" up;
	$IP netns exec $NS_NAME ip link set $VETH_NAME"b" up;

	$IPTABLES -A FORWARD -o $BASE_ETH -i $VETH_NAME"a" -j ACCEPT -m comment --comment "$NS_NAME";
	$IPTABLES -A FORWARD -i $BASE_ETH -o $VETH_NAME"a" -j ACCEPT -m comment --comment "$NS_NAME";
	$IPTABLES -t nat -A POSTROUTING -s $VETH_BACK_IP/24 -o $BASE_ETH -j MASQUERADE -m comment --comment "$NS_NAME";

	$IP netns exec $NS_NAME ip route add default via $VETH_FRONT_IP;

	#add public DNS resolver
	mkdir -p /etc/netns/$NS_NAME;
	echo "nameserver 1.1.1.1" > /etc/netns/$NS_NAME/resolv.conf;
}

function remove_veth {
	if [[ -z $NS_NAME ]]; then
		echo "namespace name is required";
		exit 1;
	fi

	$IP netns del $NS_NAME 2> /dev/null;

	while $IPTABLES -L --line-number | grep $NS_NAME > /dev/null; do
		$IPTABLES -D FORWARD $($IPTABLES -L --line-number | grep $NS_NAME | head -1 | awk '{print $1}');
	done

	while $IPTABLES -t nat -L --line-number | grep $NS_NAME > /dev/null; do
		$IPTABLES -t nat -D POSTROUTING $($IPTABLES -t nat -L --line-number | grep $NS_NAME | head -1 | awk '{print $1}');
	done
}

function print_usage {
	echo "$0 [-a <action>] [--veth-name] [--base-eth] [--ns-name <namespace name>] [--front-ip <veth-front ip>] [--back-ip <veth-back ip>]";
}

if [ $# -eq 0 ]; then
	print_usage;
	exit 1;
fi

while [[ "$1" != "" ]]; do
    case $1 in
		-a )
			shift
			ACTION=$1
			;;
		--base-eth )
			shift
			BASE_ETH=$1
			;;
		--front-ip )
			shift
			VETH_FRONT_IP=$1
			;;
		--back-ip )
			shift
			VETH_BACK_IP=$1
			;;
		--veth-name )
			shift
			VETH_NAME=$1
			;;
		--ns-name)
			shift
			NS_NAME=$1
			;;
		* )
			echo "invalid argument: $1"
			exit 1
	esac
	shift
done

if [ "$ACTION" == "create" ]; then
	create_veth;
elif [ "$ACTION" == "remove" ]; then
	remove_veth;
else
	print_usage;
fi
