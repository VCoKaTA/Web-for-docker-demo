#!/usr/bin/env python
#coding:utf-8
import sys
import os
import multiprocessing
import time
import etcd
import re
from docker import Client


local_ip = '192.168.44.113'
docker_etcd_key='/app/docker/%s/container' % local_ip

############################
#通过容器名在etcd中查找相应记录，返回结果如下
#例{'Physics_ip':'192.168.44.114','Container_name':'test1','Container_ip':'192.168.157.149','Container_vlan_gateway':'192.168.157.1','Container_create':'2015-11-17 18:12:28','Container_status':'running'}
############################
def get_etcd_info(container_name):
    etcd_client=etcd.Client(host='127.0.0.1', port=2379)
    try:
        r = etcd_client.read('%s/%s'%(docker_etcd_key,container_name), recursive=True, sorted=True)
	if r:
            if r.dir is not True and "Container_name" in r.value:
                return eval(r.value)
        else:
	    r=[]
	    return r
    except:
	r=[]	
############
##all_container函数返回所有容器的容器名和状态
##########
def all_container():
    docker_client = Client(base_url='tcp://%s:2375' % local_ip,version='1.20', timeout=10)
    docker_container=docker_client.containers(all=True)
    container=[]
    for i in docker_container:
        container.append({'Names':i['Names'][0].encode('utf-8').replace('/',''),'Status':i['Status'].encode('utf-8')})
    return container
##################
##name_list为docker容器名列表
##check_etcd函数通过name_list把在etcd中存在容器而不存在docker主机的容器信息匹配出来，并删除
#################
def check_etcd(name_list):
    try:
        etcd_client=etcd.Client(host='127.0.0.1', port=2379)
        etcd_container = etcd_client.read(docker_etcd_key, recursive=True, sorted=True)
        etcd_list = []
	if etcd_container:
            for child in etcd_container.children:
	        if child.dir is not True and "Container_name" in child.value:
		    etcd_list.append(eval(child.value))
        #print etcd_list
	for i in etcd_list:
            #print i['Container_name']
            if i['Container_name'] not in name_list:
                #r = etcd_client.delete('/app/docker/192.168.44.114/container/test1')
                #print docker_etcd_key
                r = etcd_client.delete('%s/%s'%(docker_etcd_key,i['Container_name'])) 
               # print "############delete"
               # print r
    except:
        pass
############################
##check容器，如果容器ip不存在，通过etcd的信息通过命令设置回原来的ip
############################
def set_container_ip(container_name,static_ip,gatway):
    try:
        tag = []
        cmd1 = "docker exec  %s ifconfig |grep 'inet addr'|head -n 1|awk  '{print $2}'|awk -F':' '{print $2}'" % container_name
        cmd2 = "pipework ovs1 %s %s/24@%s" % (container_name,static_ip,gatway)	
        cmd3 = "pipework ovs1 %s dhclient" % container_name
        get_ip = os.popen(cmd1).read().strip('\n')
	if not get_ip or str(get_ip) == '127.0.0.1':
           # print get_ip
            if static_ip=="127.0.0.1":
                os.popen(cmd3).read().strip('\n')
                get_ip = os.popen(cmd1).read().strip('\n')
                tag.append("ip_changed")
                tag.append(str(get_ip))
                print tag
                return tag
            else:
                os.popen(cmd2).read().strip('\n')
                tag.append('ok')
                return tag
        elif str(get_ip) != static_ip  and str(get_ip) != '127.0.0.1':
            tag.append("ip_changed")
            tag.append(str(get_ip))
            return tag
        else:
            tag.append('ok')
            return tag
        return tag
    except:
        return 'err'
####################
##更新etcd的信息
####################
def check_ip(container_name,container_status):
    etcd_client=etcd.Client(host='127.0.0.1', port=2379)
    try:
        etcd_container = etcd_client.read('%s/%s'%(docker_etcd_key,container_name), recursive=True, sorted=True)
       # print "++++++++++++++++++++++"
       # print etcd_container
    except:
        try:
            Container_ip = os.popen("docker exec  %s ifconfig |grep 'inet addr'|head -n 1|awk  '{print $2}'|awk -F':' '{print $2}'" % container_name).read().strip('\n')
            if Container_ip!="127.0.0.1":
                etcd_container_info={'Physics_ip':local_ip,'Container_name':container_name,'Container_ip':Container_ip,'Container_vlan_gateway':'192.168.157.1','Container_create':'','Container_status':'running'}
          #  print etcd_container_info
            r = etcd_client.write('%s/%s'%(docker_etcd_key,container_name),etcd_container_info)
           # print "++++++=================="
           # print r
        except:
             pass
    if etcd_container:
        if etcd_container.dir is not True and "Container_name" in etcd_container.value:
            etcd_container_info = eval(etcd_container.value)
        if etcd_container_info:
            #print etcd_container_info
            tag = set_container_ip(etcd_container_info['Container_name'],etcd_container_info['Container_ip'],etcd_container_info['Container_vlan_gateway'])
            #print tag
            if tag[0] == "ip_changed" and tag[1]:
                etcd_container_info['Container_ip']=tag[1]
                etcd_container_info['Container_status'] == "running"
                #print etcd_container_info
                try:
                    r = etcd_client.write('%s/%s'%(docker_etcd_key,container_name),etcd_container_info)
	        except:
                    pass
            else: 
                if  re.match('Exited',etcd_container_info['Status']) and etcd_container_info['Container_status'] == "running":
                    try:
                        etcd_container_info['Container_status'] = 'stopped'
                        r = etcd_client.write('%s/%s'%(docker_etcd_key,container_name),etcd_container_info)
	            except:
	                pass
                elif not re.match('Exited',etcd_container_info['Status']) and etcd_container_info['Container_status'] == "stopped":
                    try:
                        etcd_container_info['Container_status'] = 'running'
                        r = etcd_client.write('%s/%s'%(docker_etcd_key,container_name),etcd_container_info)
	            except:
	                pass
if __name__ == "__main__":
    try:
        name_list = []
        container_all = all_container()
        #print container_all
        for i in container_all:
            name_list.append(i['Names'])
        #print "###########name list"
        #print name_list
	check_etcd(name_list)
	if len(name_list) == 1:
            num=1
        elif len(name_list)>=4 and len(name_list)<=8:
            num=4
        elif len(name_list) >8 and len(name_list)<=20:
            num=8
        else:
            num=15
        pool = multiprocessing.Pool(processes=num)
        scan_result=[]
        for i in container_all:
            if not re.match('Exited',i['Status']):
                pool.apply_async(check_ip, (i['Names'],i['Status'], ))
        pool.close()
        pool.join()
            
    except:
        pass
