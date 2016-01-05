#!/bin/bash
#删除docker测试机
#docker rm `docker stop $(docker ps -a -q)`
#删除已有的openvswitch交换机
ovs-vsctl list-br|xargs -I {} ovs-vsctl del-br {}
ovs-vsctl add-br ovs1
ovs-vsctl add-port ovs1 em2
ip link set ovs1 up
ifconfig em2 0
ifconfig ovs1 192.168.157.21 netmask 255.255.255.0
