#!/bin/bash
set -e

case "$1" in
    --wait)
  WAIT=1
	;;
    --verbose)
  VERBOSE=1
  shift 1
  ;;
esac

IFNAME=$1
if [ "$2" == "-i" ]; then
  CONTAINER_IFNAME=$3
  shift 2
else
  CONTAINER_IFNAME=eth1
fi
GUESTNAME=$2
IPADDR=$(echo $3|cut -d@ -f1)
GATEWAY=$(echo $3 | grep @ | cut -d@ -f2)
MACADDR=$(echo $@ | grep '..:..:..:..:..:..' | awk '{print $NF}' )

[ "$VERBOSE" ] && {
  echo hostinterface:$IFNAME containerinterface:$CONTAINER_IFNAME guestname:$GUESTNAME ipaddr:$IPADDR gateway:$GATEWAY macaddr:$MACADDR
}

[ "$WAIT" ] && {
	while ! grep -q ^up$ /sys/class/net/$CONTAINER_IFNAME/operstate 2>/dev/null
	do sleep 1
	done
	exit 0
}

[ "$IPADDR" ] || {
    echo "Syntax:"
    echo "pipework <hostinterface> [-i containerinterface] <guest> <ipaddr>/<subnet>[@default_gateway] [macaddr]"
    echo "pipework <hostinterface> [-i containerinterface] <guest> dhcp [macaddr]"
    echo "pipework --wait"
    exit 1
}

# First step: determine type of first argument (bridge, physical interface...)
if [ -d /sys/class/net/$IFNAME ]
then
    if [ -d /sys/class/net/$IFNAME/bridge ]
    then IFTYPE=bridge
    else IFTYPE=phys
    fi
else
    case "$IFNAME" in
	br*)
	    IFTYPE=bridge
	    ;;
	*)
	    echo "I do not know how to setup interface $IFNAME."
	    exit 1
	    ;;
    esac
fi

# Second step: find the guest (for now, we only support LXC containers)
while read dev mnt fstype options dump fsck
do
    [ "$fstype" != "cgroup" ] && continue
    echo $options | grep -qw devices || continue
    CGROUPMNT=$mnt
done < /proc/mounts

[ "$CGROUPMNT" ] || {
    echo "Could not locate cgroup mount point."
    exit 1
}

N=$(find "$CGROUPMNT" -name "$GUESTNAME*" | wc -l)
case "$N" in
    0)
	echo "Could not find any container matching $GUESTNAME."
	exit 1
	;;
    1)
	true
	;;
    *)
	echo "Found more than one container matching $GUESTNAME."
	exit 1
	;;
esac

if [ "$IPADDR" = "dhcp" ]
then
    # We use udhcpc to obtain the DHCP lease, make sure it's installed.
    which udhcpc >/dev/null || {
	echo "You asked for DHCP; please install udhcpc first."
	exit 1
    }
else
    # Check if a subnet mask was provided.
    echo $IPADDR | grep -q / || {
	echo "The IP address should include a netmask."
	echo "Maybe you meant $IPADDR/24 ?"
	exit 1
    }
fi

NSPID=$(head -n 1 $(find "$CGROUPMNT" -name "$GUESTNAME*" | head -n 1)/tasks)
[ "$NSPID" ] || {
    echo "Could not find a process inside container $GUESTNAME."
    exit 1
}

[ "$VERBOSE" ] && {
  echo NSPID: $NSPID
}

mkdir -p /var/run/netns
rm -f /var/run/netns/$NSPID
ln -s /proc/$NSPID/ns/net /var/run/netns/$NSPID


# Check if we need to create a bridge.
[ $IFTYPE = bridge ] && [ ! -d /sys/class/net/$IFNAME ] && {
    ip link add $IFNAME type bridge
    ip link set $IFNAME up
}

# If it's a bridge, we need to create a veth pair
[ $IFTYPE = bridge ] && {
    LOCAL_IFNAME=vethl$NSPID$CONTAINER_IFNAME
    GUEST_IFNAME=vethg$NSPID$CONTAINER_IFNAME
    ip link add name $LOCAL_IFNAME type veth peer name $GUEST_IFNAME
    ip link set $LOCAL_IFNAME master $IFNAME
    ip link set $LOCAL_IFNAME up
}

# If it's a physical interface, create a macvlan subinterface
[ $IFTYPE = phys ] && {
    GUEST_IFNAME=macvlan$NSPID$CONTAINER_IFNAME
    ip link add link $IFNAME dev $GUEST_IFNAME type macvlan mode bridge
    ip link set $IFNAME up
}

ip link set $GUEST_IFNAME netns $NSPID
ip netns exec $NSPID ip link set $GUEST_IFNAME name $CONTAINER_IFNAME
[ "$MACADDR" ] && ip netns exec $NSPID ip link set $CONTAINER_IFNAME address $MACADDR
if [ "$IPADDR" = "dhcp" ]
then
    ip netns exec $NSPID udhcpc -qi $CONTAINER_IFNAME
else
    ip netns exec $NSPID ip addr add $IPADDR dev $CONTAINER_IFNAME
    ip netns exec $NSPID ip link set $CONTAINER_IFNAME up
    [ "$GATEWAY" ] && {
	ip netns exec $NSPID ip route delete default
	ip netns exec $NSPID ip route add default via $GATEWAY
    }
fi

exit 0