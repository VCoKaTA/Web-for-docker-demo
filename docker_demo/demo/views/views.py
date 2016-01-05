#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
import types ,time,threading
import sys
import os,re 
import multiprocessing
import subprocess
from demo import models
import traceback
from Docker_api import DockerApi
import paramiko
import json
from django import forms
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=u'原始密码',error_messages={'required':'请输入原始密码'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password1 = forms.CharField(label=u'新密码',error_messages={'required':'请输入新密码'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(label=u'重复输入',error_messages={'required':'请重复新输入密码'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(u'原密码错误')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if len(password1)<6:
            raise forms.ValidationError(u'密码必须大于6位')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次密码输入不一致')
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
def login(request):
	return render_to_response('docker/login.html')
def login_auth(request):
	try:
		USERNAME,PASSWORD = request.POST.get('Username'),request.POST.get('Password')
		user_auth = auth.authenticate(username=USERNAME, password = PASSWORD)
		print '_'*30,user_auth
		
		if user_auth is not None: #username and passwd correct 
			auth.login(request, user_auth)
			return HttpResponseRedirect(reverse('dockerindexurl'))
		else:
			return render_to_response('docker/login.html', {'login_err': 'Wrong username or password!'})
	except:
		print traceback.format_exc()
		return HttpResponse('error')
def logout(request):
	try:
		auth.logout(request)
		return HttpResponseRedirect('/login/')
	except:
		print traceback.format_exc()
		return HttpResponse('error')
		
def ChangePassword(request):
    # print request.META.get('HTTP_REFERER', '/')
    if request.method=='POST':
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('logouturl'))
            return HttpResponseRedirect('/login')
    else:
        form = ChangePasswordForm(user=request.user)

    kwvars = {
        'form':form,
        'request':request,
    }

    return render_to_response('docker/password.change.html',kwvars,RequestContext(request))
#############
#匹配文本file中的ip
############
def match_ip(file):
	tag = reg='\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
	result = re.findall(reg,file,re.I)
	if result:
		for i in result:
			if i != '127.0.0.1':
				return i
			else:
				continue
	else:
		return None
##################
#unix时间戳转换
##################
def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    ## 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt

####################
#多线程更新容器信息
####################
def Refresh_container():
	nodes = models.Node.objects.filter(node_type='node')
	print '刷新容器'
	if nodes:
		num=len(nodes)
		threads = []
		try:
			# pool = multiprocessing.Pool(processes=num)
			for i in nodes:
				# pool.apply_async(check_containers, (i.node_ip,))
				# pool.close()
				# pool.join()
				t = threading.Thread(target=check_containers,args=(i.node_ip,))
				threads.append(t)
			for i,t in zip(range(num),threads):
				t.start()
				if i % 10 == 0:
					time.sleep(0.05)
			for t in threads:
				t.join()
		except:
			pass
#############
#容器更新函数
##############
def check_containers(node_ip):
	if node_ip:
		name_list = []
		try:
			docker_cli = DockerApi(node_ip)
			containers = docker_cli.containers()
			# print containers
		except:
			# pass
			print traceback.format_exc()
		con_info = {}
		for i in containers:
			if  re.match('Exited',i['Status']):
				con_info['status'] = False
			else:
				con_info['status'] = True
			con_info['image'] = i['Image'].encode('utf-8')
			con_info['container_name'] = i['Names'][0].encode('utf-8').replace('/','')
			name_list.append(con_info['container_name'])
			con_info['create_time'] = timestamp_datetime(int(i['Created']))
			con_info['container_id'] = i['Id'].encode('utf-8')
			if con_info['status']:
				con_info['container_ip'] = match_ip(docker_cli.exec_start(docker_cli.exec_create(con_info['container_name'],'ip addr')['Id']))
			else:
				con_info['container_ip'] = ''
			container = models.Containers.objects.filter(node__node_ip=node_ip).filter(container_name=con_info['container_name'])
			if container:
				if container[0].status != con_info['status']:
					container[0].status = con_info['status']
				if container[0].container_ip != con_info['container_ip'] and con_info['container_ip']:
					container[0].container_ip = con_info['container_ip']
			else:
				try:
					models.Containers.objects.create(user=models.User.objects.get(username='root'),container_name=con_info['container_name'],container_id=con_info['container_id'],container_ip=con_info['container_ip'],image=con_info['image'],create_time=con_info['create_time'],node=models.Node.objects.get(node_ip=node_ip),status= con_info['status'])
				except:
					print traceback.format_exc()
		try:
			container_list = models.Containers.objects.filter(node__node_ip=node_ip).filter(node__node_ip=node_ip)
			if container_list:
				for i in container_list:
					if i.container_name not in name_list:
						i.delete()
		except:
			# pass
			print traceback.format_exc()
####################
#多线程更新images信息
####################
def Refresh_image():
	nodes = models.Node.objects.all()
	if nodes:
		num=len(nodes)
		threads = []
		try:
			# pool = multiprocessing.Pool(processes=num)
			for i in nodes:
				# pool.apply_async(check_images, (i.node_ip,i.node_type,))
				# pool.close()
				# pool.join()
				t = threading.Thread(target=check_images, args=(i.node_ip,i.node_type))
				threads.append(t)
			for i,t in zip(range(num),threads):
				t.start()
				if i % 10 == 0:
					time.sleep(0.05)
			for t in threads:
				t.join()
		except:
			# pass
			print traceback.format_exc()
#############
#images更新函数
##############
def check_images(node_ip,tag):
	if node_ip:
		name_list = []
		try:
			docker_cli = DockerApi(node_ip)
			images = docker_cli.images()
		except:
			# pass
			print traceback.format_exc()
		image_info = {}
		image_name = []
		for i in images:
			image_info['size']=str(float('%.2f' % (float(i['VirtualSize'])/1000000)))
			for j in i['RepoTags']:
				image_name.append(j.encode('utf-8'))
				name_list.append(j.encode('utf-8'))
			image_info['image_id']=i['Id'].encode('utf-8')
			for i in image_name:
				image = models.Images.objects.filter(node__node_ip=node_ip).filter(repository=i).filter(image_type=False)
				if image:
					if image[0].repository == i and image[0].image_id != image_info['image_id']:
						image[0].image_id = image_info['image_id']
						image[0].size = image_info['size']
				else:
					try:
						models.Images.objects.create(repository=i,image_id=image_info['image_id'],size=image_info['size'],node=models.Node.objects.get(node_ip=node_ip),image_type=False)
					except:
						# pass
						print traceback.format_exc()
		try:
			image_list = models.Images.objects.filter(node__node_ip=node_ip).filter(image_type=False)
			if image_list:
				for i in image_list:
					if i.repository not in name_list:
						i.delete()
		except:
			# pass
			print traceback.format_exc()
		if tag == 'registory':
			name_list = []
			try:
				images = subprocess.Popen("curl -X GET %s:5000/v1/search" % node_ip , shell=True,stdout=subprocess.PIPE).stdout.readlines()
				if images:
					# print type(images)
					# print images
					images = eval(images[0])['results']
					for i in images:
						image_info['repository'] = i['name'].encode('utf-8')
						name_list.append(image_info['repository'])
						image = models.Images.objects.filter(node__node_ip=node_ip).filter(repository=image_info['repository']).filter(image_type=True)
						if not image:
							try:
								models.Images.objects.create(repository=image_info['repository'],node=models.Node.objects.get(node_ip=node_ip),image_type=True)
							except:
								# pass
								print traceback.format_exc()
					try:
						image_list = models.Images.objects.filter(node__node_ip=node_ip).filter(node__node_ip=node_ip).filter(image_type=True)
						if image_list:
							for i in image_list:
								if i.repository not in name_list:
									i.delete()
					except:
						# pass
						print traceback.format_exc()
			except:
				# pass
				print traceback.format_exc()
	else:
		pass

@login_required(login_url='/login/')
# @PermissionVerify()
#刷新各节点的image和容器信息
def index(request):
	user = request.user
	try:
		pull_images()
		Refresh_image()
		Refresh_container()
	except:
		# pass
		print traceback.format_exc()
	return render_to_response('docker/index.html',{'user':user})






@login_required
# @PermissionVerify()
def container_list(request):
	user = request.user
	if user.is_superuser:
		containers = models.Containers.objects.all()
	else:
		containers = models.Containers.objects.filter(user=user)
	err = ''
	if containers:
		return render_to_response('docker/listdocker.html',{'user':user,'containers':containers,'err':err})
	else:
		err = u'没有容器或者没有权限！'
		return render_to_response('docker/listdocker.html',{'user':user,'err':err})
@login_required
# @PermissionVerify()
def container_create(request):
	user = request.user		
	try:
		if request.method == 'POST' and request.POST.get('container') and request.POST.get('image'):
			container = request.POST.get('container').encode("utf-8")
			image = request.POST.get('image').encode("utf-8")
			node = request.POST.get('node').encode("utf-8")
			
			if node == "random":
				try:
					create_node = models.Node.objects.get(weight_type="True")
					docker_cli = DockerApi(create_node.node_ip)
					registry_node = models.Node.objects.get(node_type="registory")
					repository="%s:5000/%s:latest" % (registry_node.node_ip,image)
					if not models.Images.objects.filter(repository=repository).filter(node__node_ip=create_node.node_ip):
						images = docker_cli.pull("%s:5000/%s" % (registry_node.node_ip,image))
						# print images
					cmd = "/usr/bin/sh /root/create_docker_container_use_dhcp_ip.sh  %s %s:5000/%s" % (container,registry_node.node_ip,image)
					# cmd ="ifconfig"
					# print cmd
					ssh_docker = paramiko.SSHClient()  
					ssh_docker.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
					ssh_docker.connect(create_node.node_ip,22,"root",create_node.root_password,timeout=5)
					stdin, stdout, stderr = ssh_docker.exec_command(cmd)  
					# print "#####"
					# stdin.write("Y")   #简单交互，输入 ‘Y’   
					create_container_info = stdout.readlines()
					print create_container_info
					try:
						for info in create_container_info:
							# print type(info)
							# print info
							if re.search('Container_name',info):
								tag = 0
								node_count = models.Node.objects.all().count()
								tag = int(create_node.weight)%node_count + 1
								if tag == node_count:
									tag = 1
								# print create_node.node_ip
								# print create_node.weight_type
								create_node.weight_type=False
								create_node.save()
								# print create_node.node_ip
								# print create_node.weight_type
								now_create_node = models.Node.objects.get(weight=tag)
								# print now_create_node.node_ip
								# print now_create_node.weight_type
								now_create_node.weight_type=True
								now_create_node.save()
								# print now_create_node.node_ip
								# print now_create_node.weight_type
								create_container = eval(info.strip('\n'))
								containers = docker_cli.containers()
								cont_id = ''
								cont_image = ''
								for i in containers:
									if i['Names'][0].encode('utf-8').replace('/','') == container:
										cont_id=i['Id'].encode('utf-8')
										cont_image = i['Image'].encode('utf-8')
								if cont_id:
									models.Containers.objects.create(user=user,container_name=container,container_id=cont_id,container_ip = create_container["Container_ip"],image=cont_image,create_time=create_container["Container_create"],node=create_node)
					except:
						print traceback.format_exc()
				except:
					print traceback.format_exc()
			else:
				try:
					create_node = models.Node.objects.get(node_ip=node)
					docker_cli = DockerApi(create_node.node_ip)
					registry_node = models.Node.objects.get(node_type="registory")
					repository="%s:5000/%s:latest" % (registry_node.node_ip,image)
					if not models.Images.objects.filter(repository=repository).filter(node__node_ip=create_node.node_ip):
						images = docker_cli.pull("%s:5000/%s" % (registry_node.node_ip,image))
						# print images
					cmd = "/usr/bin/sh /root/create_docker_container_use_dhcp_ip.sh  %s %s:5000/%s" % (container,registry_node.node_ip,image)
					# cmd ="ifconfig"
					ssh_docker = paramiko.SSHClient()  
					ssh_docker.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
					ssh_docker.connect(create_node.node_ip,22,"root",create_node.root_password,timeout=5)
					stdin, stdout, stderr = ssh_docker.exec_command(cmd)  
					#stdin.write("Y")   #简单交互，输入 ‘Y’   
					create_container_info = stdout.readlines()
					for info in create_container_info:
						if  re.search('Container_name',info): 
							create_container = eval(info.strip('\n'))
							containers = docker_cli.containers()
							cont_id = ''
							cont_image = ''
							for i in containers:
								if i['Names'][0].encode('utf-8').replace('/','') == container:
									cont_id=i['Id'].encode('utf-8')
									cont_image = i['Image'].encode('utf-8')
							if cont_id:
								models.Containers.objects.create(user=user,container_name=container,container_id=cont_id,container_ip = create_container["Container_ip"],image=cont_image,create_time=create_container["Container_create"],node=create_node)
				except:
					print traceback.format_exc()
			return HttpResponseRedirect(reverse('listcontainerurl'))
		else:
			nodes = models.Node.objects.filter(node_type='node')
			images = models.Images.objects.filter(image_type='True')
			return render_to_response('docker/addcontainer.html',{'user':user,'nodes':nodes,'images':images})
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listcontainerurl'))
@login_required
# @PermissionVerify()		
def container_delete(request,id):
	user = request.user
	container = models.Containers.objects.get(id=int(id))
	try:
		if container:
			docker_cli = DockerApi(container.node.node_ip)
			docker_cli.remove_container(container.container_name)
			container.delete()
			return HttpResponseRedirect(reverse('listcontainerurl'))
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listcontainerurl'))
@login_required
# @PermissionVerify()		
def container_restart(request,id):
	user = request.user
	container = models.Containers.objects.get(id=int(id))
	try:
		if container:
			docker_cli = DockerApi(container.node.node_ip)
			docker_cli.restart(container.container_name)
			container.status = True
			return HttpResponseRedirect(reverse('listcontainerurl'))
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listcontainerurl'))
@login_required
# @PermissionVerify()		
def container_start(request,id):
	user = request.user
	container = models.Containers.objects.get(id=int(id))
	try:
		if container:
			docker_cli = DockerApi(container.node.node_ip)
			containers = docker_cli.containers()
			docker_cli.start(container.container_name)
			container.status = True
			return HttpResponseRedirect(reverse('listcontainerurl'))
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listcontainerurl'))
@login_required
# @PermissionVerify()		
def container_stop(request,id):
	user = request.user
	container = models.Containers.objects.get(id=int(id))
	try:
		if container:
			docker_cli = DockerApi(container.node.node_ip)
			docker_cli.stop(container.container_name)
			container.status = False
			return HttpResponseRedirect(reverse('listcontainerurl'))
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listcontainerurl'))

def pull_images():
	try:
		registry_images = models.Images.objects.filter(image_type=True)
		nodes=models.Node.objects.filter(node_type="node")
		registry_node = models.Node.objects.get(node_type="registory")
		for i in registry_images:
			# print i.repository
			for j in nodes:
				repository="%s:5000/%s:latest" % (registry_node.node_ip,i.repository)
				if not models.Images.objects.filter(node__node_ip=j.node_ip).filter(repository=repository):
					docker_cli = DockerApi(j.node_ip)
					# print j.node_ip
					images = docker_cli.pull("%s:5000/%s" % (registry_node.node_ip,i.repository))
	except:
		print traceback.format_exc()
@login_required
# @PermissionVerify()			
def image_commit(request,id):
	user = request.user
	container = models.Containers.objects.get(id=int(id))
	registry_node = models.Node.objects.get(node_type="registory")
	try:
		if request.method == 'POST' and request.POST.get('image_name'):
			image_name = request.POST.get('image_name').encode("utf-8")
			repository = "%s:5000/%s" % (registry_node.node_ip,image_name)
			# print image_name
			if container:
				docker_cli = DockerApi(container.node.node_ip)
				docker_cli.commit(container.container_name,repository)
				docker_cli.push(repository)
				pull_images()
				Refresh_image()
			return HttpResponseRedirect(reverse('listimageurl'))
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listimageurl'))
@login_required
# @PermissionVerify()	
def image_build(request):
	user = request.user
	registry_node = models.Node.objects.get(node_type="registory")
	try:
		if request.method == 'POST':
			data = ''
			dockerfile = request.POST.get('dockerfile').encode("utf-8")
			# datapath = os.getcwd() + '/auto_docker/views/dockerfile1'
			# f = open(datapath,'r+')
			# data=f.write(dockerfile)
			# f.close()
			# print dockerfile
			# print type(dockerfile)
			image_name = request.POST.get('image_name').encode("utf-8")
			tag = "%s:5000/%s" % (registry_node.node_ip,image_name)
			# print tag
			docker_cli = DockerApi(registry_node.node_ip)
			# print docker_cli.build(dockerfile,tag)
			# print "+++++++++++++++++++++++++++++"
			# print docker_cli.push(tag)
			for i in docker_cli.build(dockerfile,tag):
				data = data + i
			data +="Push image: %s \n\n" % tag
			for i in docker_cli.push(tag):
				data = data + i 
			pull_images()
			Refresh_image()
			return render_to_response('docker/buildresult.html',{'user':user,'data':data})
		else:
			return render_to_response('docker/buildimage.html',{'user':user})
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listimageurl'))
# @PermissionVerify()	
def image_refresh(request):
	try:
		pull_images()
		Refresh_image()
		return HttpResponseRedirect(reverse('listimageurl'))
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listimageurl'))
# @PermissionVerify()	
def dockerfile(request):
	try:
		datapath = os.getcwd() + '/demo/views/dockerfile'
		print datapath
		f = open(datapath,'r')
		data=f.read()
		f.close()
		return HttpResponse(data)
	except:
		print traceback.format_exc()
		return HttpResponseRedirect(reverse('listimageurl'))
@login_required
# @PermissionVerify()
def image_list(request):
	user = request.user
	images = models.Images.objects.all().order_by("node")
	err = ''
	if images:
		return render_to_response('docker/listimages.html',{'user':user,'images':images,'err':err})
	else:
		err = u'没有镜像，请创建镜像！'
		return render_to_response('docker/listimages.html',{'user':user,'err':err})
		
@login_required
# @PermissionVerify()
def image_delete(request,id):
	user = request.user
	image = models.Images.objects.get(id=int(id))
	if image:
		if image.image_type:
			try:
				info = subprocess.Popen("curl -v --raw -X DELETE %s:5000/v1/repositories/%s/" % (image.node.node_ip,image.repository) , shell=True,stdout=subprocess.PIPE).stdout.readlines()
				str_info = ''
				for i in info:
					str_info += i;
				if re.findall('200 OK',str_info):
					image.delete()
					Refresh_image()
					return HttpResponseRedirect(reverse('listimageurl'))
				else:
					err = "删除%s失败" % image.repository
					return render_to_response('docker/listimages.html',{'user':user,'err':err})
				
			except:
				print traceback.format_exc()
				err = "删除%s失败" % image.repository
				return HttpResponseRedirect(reverse('listimageurl'))
				# return render_to_response('auto_docker/listimages.html',{'user':user,'err':err})
		else:
			try:
				docker_cli = DockerApi(image.node.node_ip)
				docker_cli.remove_image(image.repository)
				Refresh_image()
				return HttpResponseRedirect(reverse('listimageurl'))
			except:
				print traceback.format_exc()
				return HttpResponseRedirect(reverse('listimageurl'))
