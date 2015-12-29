# encoding: utf-8
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

###########
##node节点表，包括主机节点和私有仓库节点
###########
class Node(models.Model):
	node_ip = models.CharField(max_length=200,unique=True)
	node_name = models.CharField(max_length=100,null=True,blank=True)
	weight = models.SmallIntegerField(u'节点权重')
	weight_choices = ((True, 'YES'),
				(False, 'NO'),
				)
	weight_type = models.BooleanField(u'容器创建于本节点',choices=weight_choices, default=False)
	type_node = (('node', u'节点'),
				('registory', u'仓库节点'),
				)
	node_type = models.CharField(u'节点类型',choices=type_node,max_length=64, default='node')
	create_image_choices = ((True, 'YES'),
				(False, 'NO'),)
	create_image = models.BooleanField(u'镜像生成节点',choices=create_image_choices, default=False)
	root_password = models.CharField(u'主机密码', max_length=200)
	class Meta:
		verbose_name = '节点表'
		verbose_name_plural = "节点表"
	def __unicode__(self):
		return self.node_ip

################
##镜像列表
################
class Images(models.Model):
	repository =  models.CharField(max_length=200)
	image_id =  models.CharField(max_length=200,blank=True,null=True)
	size = models.CharField(max_length=10,blank=True,null=True)
	function = models.CharField(max_length=32,blank=True,null=True)
	node = models.ForeignKey(Node)
	image_choices = ((True, u'仓库'),
				(False, u'本地'),)
	image_type= models.BooleanField(u'镜像所在节点类型',choices=image_choices, default=False)
	class Meta:
		verbose_name = '镜像列表'
		verbose_name_plural = "镜像列表"
	def __unicode__(self):
		return '%s-%s' % (self.repository,self.node.node_ip)

########################
##容器列表
########################
class Containers(models.Model):
	user = models.ForeignKey(User,blank=True,null=True)
	container_name = models.CharField(max_length=100)
	# container_tag = models.CharField(max_length=50,unique=True)
	container_id = models.CharField(max_length=200,blank=True,null=True)
	container_ip = models.CharField(max_length=200,blank=True,null=True)
	image = models.CharField(max_length=100)
	function = models.CharField(max_length=32,blank=True,null=True)
	create_time =  models.CharField(max_length=32,blank=True,null=True)
	node = models.ForeignKey(Node)
	status_choices = ((True, 'running'),
				(False, 'stopped'),)
	status = models.BooleanField(u'容器状态',choices=status_choices, default=True)
	class Meta:
		verbose_name = '容器列表'
		verbose_name_plural = "容器列表"
	def __unicode__(self):
		return self.container_name