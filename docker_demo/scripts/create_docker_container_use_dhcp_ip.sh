#!/bin/bash
#this script is create new docker container and use pipework add static ip/dhcp ip,when container is restart,it also use last static ip
container=$1
images=$2
#ip_pool='192.168.157.1/24'
bridge=ovs1
gateway_ip='192.168.157.1'
local_ip=`ip a | grep 'inet'| grep -Ev '(127|117|211|172|::1|fe)' |awk '{print $2}'|head -n 1|awk -F"/" '{print $1}'`
if [ -z $1 ] || [ -z $2 ]; then
  echo "Usage: container_name container_image vlan_tag(default:1)"
  echo "Example: I want create new docker container test1 centos6:latest supervisord "
  echo "The command is: bash `basename $0` test1 centos6:latest supervisord"
  exit 1
fi
[ `docker ps -a|grep -v "NAMES"|awk '{print $NF}'|grep "$container" &>>/dev/null && echo 0 || echo 1` -eq 0 ] && echo "The container $container is exist!" && exit 1
[ `which pipework &>/dev/null && echo 0|| echo 1` -eq 1 ] && echo "I can't find pipework,please install it!" && exit 1

#create new docker container
docker run --restart always -d --net="none" --name="$container" $images &>>/dev/null
#check openvswitch bridge exist
if [ `ovs-vsctl  list-br |grep ${bridge} &>/dev/null && echo 0|| echo 1` -eq 1 ];then
  sh /root/openvswitch_docker.sh
fi

#calculate new ip
sleep 1
tag=1
while [[ ${tag} == 1 ]]
do
  #docker restart $container &>>/dev/null
  docker restart $container 
  create_time=`date +"%Y-%m-%d %T"`
  `which pipework` $bridge $container dhclient
  if [ `docker exec  ${container} ip a |grep "inet"|grep -Ev '(127|117|211|172|::1|fe)'  &>>/dev/null && echo 0 || echo 1` -eq 0 ];then
    tag=0
  fi
done
new_container_ip=$(awk -v ip=`docker exec  ${container} ip a | grep 'inet'| grep -Ev '(127|117|211|172|::1|fe)' |awk '{print $2}'|head -n 1|awk -F"/" '{print $1}'` 'BEGIN{print ip}')
etcdctl set /app/docker/${local_ip}/container/${container} "{'Physics_ip':'${local_ip}','Container_name':'${container}','Container_ip':'${new_container_ip}','Container_vlan_gateway':'${gateway_ip}','Container_create':'${create_time}','Container_status':'running'}"
