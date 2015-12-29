#coding=utf-8
#/usr/bin/env python
from docker import Client
from io import BytesIO
import traceback
class DockerApi(object):
	""" """
	def __init__(self,url):
		self.url = url
		self.cli = Client(base_url='%s:2375'%self.url,version='1.20', timeout=120)

################################################
#列出容器
# quiet (bool): Only display numeric Ids
# all (bool): Show all containers. Only running containers are shown by default
# trunc (bool): Truncate output
# latest (bool): Show only the latest created container, include non-running ones.
# since (str): Show only containers created since Id or Name, include non-running ones
# before (str): Show only container created before Id or Name, include non-running ones
# limit (int): Show limit last created containers, include non-running ones
# size (bool): Display sizes
# filters (dict): Filters to be processed on the image list. Available filters:
# exited (int): Only containers with specified exit code
# status (str): One of restarting, running, paused, exited
# label (str): format either "key" or "key=value"
# Returns (dict): The system's containers

# >>> from docker import Client
# >>> cli = Client(base_url='tcp://127.0.0.1:2375')
# >>> cli.containers()
# [{'Command': '/bin/sleep 30',
  # 'Created': 1412574844,
  # 'Id': '6e276c9e6e5759e12a6a9214efec6439f80b4f37618e1a6547f28a3da34db07a',
  # 'Image': 'busybox:buildroot-2014.02',
  # 'Names': ['/grave_mayer'],
  # 'Ports': [],
  # 'Status': 'Up 1 seconds'}]
#################################################
	def containers(self):
		container_all = self.cli.containers(all=True)
		return container_all

###############################################
# exec_create

# Sets up an exec instance in a running container.

# Params:

# container (str): Target container where exec instance will be created
# cmd (str or list): Command to be executed
# stdout (bool): Attach to stdout of the exec command if true. Default: True
# stderr (bool): Attach to stderr of the exec command if true. Default: True
# tty (bool): Allocate a pseudo-TTY. Default: False
# user (str): User to execute command as. Default: root
# Returns (dict): A dictionary with an exec 'Id' key.	
###############################################	
	def exec_create(self,container_name,cmd):
		return self.cli.exec_create(container=container_name,cmd=cmd)
###############################################	
# exec_start

# Start a previously set up exec instance.

# Params:

# exec_id (str): ID of the exec instance
# detach (bool): If true, detach from the exec command. Default: False
# tty (bool): Allocate a pseudo-TTY. Default: False
# stream (bool): Stream response data. Default: False
###############################################	
	def exec_start(self,exec_id):
		return self.cli.exec_start(exec_id=exec_id)
	
#################################################
#创建容器
# image (str): The image to run
# command (str or list): The command to be run in the container
# hostname (str): Optional hostname for the container
# user (str or int): Username or UID
# detach (bool): Detached mode: run container in the background and print new container Id
# stdin_open (bool): Keep STDIN open even if not attached
# tty (bool): Allocate a pseudo-TTY
# mem_limit (float or str): Memory limit (format: [number][optional unit], where unit = b, k, m, or g)
# ports (list of ints): A list of port numbers
# environment (dict or list): A dictionary or a list of strings in the following format ["PASSWORD=xxx"] or {"PASSWORD": "xxx"}.
# dns (list): DNS name servers
# volumes (str or list):
# volumes_from (str or list): List of container names or Ids to get volumes from. Optionally a single string joining container id's with commas
# network_disabled (bool): Disable networking
# name (str): A name for the container
# entrypoint (str or list): An entrypoint
# cpu_shares (int): CPU shares (relative weight)
# working_dir (str): Path to the working directory
# domainname (str or list): Set custom DNS search domains
# memswap_limit (int):
# host_config (dict): A HostConfig dictionary
# mac_address (str): The Mac Address to assign the container
# labels (dict or list): A dictionary of name-value labels (e.g. {"label1": "value1", "label2": "value2"}) or a list of names of labels to set with empty values (e.g. ["label1", "label2"])
# volume_driver (str): The name of a volume driver/plugin.
# Returns (dict): A dictionary with an image 'Id' key and a 'Warnings' key.

# >>> from docker import Client
# >>> cli = Client(base_url='tcp://127.0.0.1:2375')
# >>> container = cli.create_container(image='busybox:latest', command='/bin/sleep 30')
# >>> print(container)
# {'Id': '8a61192da2b3bb2d922875585e29b74ec0dc4e0117fcbf84c962204e97564cd7',
 # 'Warnings': None}
########################################################
	def create_container(self,image,command,password):
		try:
			container = self.cli.create_container(image=image,command=command,environment={"PASSWORD": password})
			return container
		except:
			return None

##########################################################
# remove_container
# Remove a container. Similar to the docker rm command.
# Params:
# container (str): The container to remove
# v (bool): Remove the volumes associated with the container
# link (bool): Remove the specified link and not the underlying container
# force (bool): Force the removal of a running container (uses SIGKILL)
##########################################################
	def remove_container(self,container):
		return self.cli.remove_container(container=container,force=True)

##########################################################
# container (str): The container to start
# response = cli.start(container=container.get('Id'))
# >>> print(response)
##########################################################
	def start(self,container_name):
		try:
			req = self.cli.start(container=container_name)
			return rep
		except:
			return None
##########################################################
# container (str): The container to stop
# timeout (int): Timeout in seconds to wait for the container to stop before sending a SIGKILL
##########################################################
	def stop(self,container_name):
		try:
			req = self.cli.stop(container=container_name)
			return rep
		except:
			return None
##########################################################
#重启
#Restart a container. Similar to the docker restart command.
# If container a dict, the Id key is used.

# Params:

# container (str or dict): The container to restart
# timeout (int): Number of seconds to try to stop for before killing the container. Once killed it will then be restarted. Default is 10 seconds.
###########################################################
	def restart(self,container_name):
		try:
			req = self.cli.restart(container=container_name)
			return rep
		except:
			return None
################################################
# images
# List images. Identical to the docker images command.
# Params:
# name (str): Only show images belonging to the repository name
# quiet (bool): Only show numeric Ids. Returns a list
# all (bool): Show all images (by default filter out the intermediate image layers)
# filters (dict): Filters to be processed on the image list. Available filters:
# dangling (bool)
# label (str): format either "key" or "key=value"
# Returns (dict or list): A list if quiet=True, otherwise a di
################################################
	def images(self):
		# print type(self.cli.images())
		return self.cli.images()
		
##########################################################
# remove_image
# Remove an image. Similar to the docker rmi command.
# Params:
# image (str): The image to remove
# force (bool): Force removal of the image
# noprune (bool): Do not delete untagged parents
##########################################################
	def remove_image(self,image):
		# print type(self.cli.images())
		return self.cli.remove_image(image=image,force=True)


#########################################################
# path (str): Path to the directory containing the Dockerfile
# tag (str): A tag to add to the final image
# quiet (bool): Whether to return the status
# fileobj: A file object to use as the Dockerfile. (Or a file-like object)
# nocache (bool): Don't use the cache when set to True
# rm (bool): Remove intermediate containers. The docker build command now defaults to --rm=true, but we have kept the old default of False to preserve backward compatibility
# stream (bool): Deprecated for API version > 1.8 (always True). Return a blocking generator you can iterate over to retrieve build output as it happens
# timeout (int): HTTP timeout
# custom_context (bool): Optional if using fileobj
# encoding (str): The encoding for a stream. Set to gzip for compressing
# pull (bool): Downloads any updates to the FROM image in Dockerfiles
# forcerm (bool): Always remove intermediate containers, even after unsuccessful builds
# dockerfile (str): path within the build context to the Dockerfile
# container_limits (dict): A dictionary of limits applied to each container created by the build process. Valid keys:
# memory (int): set memory limit for build
# memswap (int): Total memory (memory + swap), -1 to disable swap
# cpushares (int): CPU shares (relative weight)
# cpusetcpus (str): CPUs in which to allow execution, e.g., "0-3", "0,1"
# decode (bool): If set to True, the returned stream will be decoded into dicts on the fly. Default False.

# >>> from io import BytesIO
# >>> from docker import Client
# >>> dockerfile = '''
# ... # Shared Volume
# ... FROM busybox:buildroot-2014.02
# ... MAINTAINER first last, first.last@yourdomain.com
# ... VOLUME /data
# ... CMD ["/bin/sh"]
# ... '''
# >>> f = BytesIO(dockerfile.encode('utf-8'))
# >>> cli = Client(base_url='tcp://127.0.0.1:2375')
# >>> response = [line for line in cli.build(
# ...     fileobj=f, rm=True, tag='yourname/volume'
# ... )]
# >>> response
# ['{"stream":" ---\\u003e a9eb17255234\\n"}',


########################################################################
	def build(self,dockerfile,tag):
		try:
			f = BytesIO(dockerfile.encode('utf-8'))
			res = [line for line in self.cli.build(fileobj=f, rm=True, tag=tag)]
			return res
		except:
			print traceback.format_exc()
			return None
###########################################################################
#commit
# container (str): The image hash of the container
# repository (str): The repository to push the image to
# tag (str): The tag to push
# message (str): A commit message
# author (str): The name of the author
# conf (dict): The configuration for the container. See the Docker remote api for full details.
###########################################################################
	def commit(self,container,repository):
		try:
			res = self.cli.commit(container=container,repository=repository)
			return res
		except:
			return None



############################################################################
#pull
# repository (str): The repository to pull
# tag (str): The tag to pull
# stream (bool): Stream the output as a generator
# insecure_registry (bool): Use an insecure registry
# auth_config (dict): Override the credentials that Client.login has set for this request  auth_config should contain the username and password keys to be valid.
# Returns (generator or str): The output

# >>> from docker import Client
# >>> cli = Client(base_url='tcp://127.0.0.1:2375')
# >>> for line in cli.pull('busybox', stream=True):
# ...     print(json.dumps(json.loads(line), indent=4))
# {
    # "status": "Pulling image (latest) from busybox",
    # "progressDetail": {},
    # "id": "e72ac664f4f0"
# }
# {
    # "status": "Pulling image (latest) from busybox, endpoint: ...",
    # "progressDetail": {},
    # "id": "e72ac664f4f0"
# }
############################################################################
	def pull(self,repository):
		try:
			# res = cli.pull(repository,stream=True)
			res =  [line for line in self.cli.pull(repository,stream=True)]
			return res
		except:
			print traceback.format_exc()
			return None


############################################################################
#push
# repository (str): The repository to push to
# tag (str): An optional tag to push
# stream (bool): Stream the output as a blocking generator
# insecure_registry (bool): Use http:// to connect to the registry
# Returns (generator or str): The output of the upload

# >>> from docker import Client
# >>> cli = Client(base_url='tcp://127.0.0.1:2375')
# >>> response = [line for line in cli.push('yourname/app', stream=True)]
# >>> response
# ['{"status":"Pushing repository yourname/app (1 tags)"}\\n',
 # '{"status":"Pushing","progressDetail":{},"id":"511136ea3c5a"}\\n',
 # '{"status":"Image already pushed, skipping","progressDetail":{},
    # "id":"511136ea3c5a"}\\n',
 # ...
 # '{"status":"Pushing tag for rev [918af568e6e5] on {
    # https://cdn-registry-1.docker.io/v1/repositories/
    # yourname/app/tags/latest}"}\\n']
############################################################################
	def push(self,repository):
		try:
			# res = cli.push(repository,stream=True)
			res = [line for line in self.cli.push(repository =repository, stream=True)]
			return res
		except:
			print traceback.format_exc()
			return None


############################
#delete images from registry
# After that you can use Registry API to check it exists in your private docker registry

# $ curl -X GET localhost:5000/v1/repositories/ubuntu/tags
# {"latest": "e54ca5efa2e962582a223ca9810f7f1b62ea9b5c3975d14a5da79d3bf6020f37"}
# Now I can delete the tag using that API !!

# $ curl -X DELETE localhost:5000/v1/repositories/ubuntu/tags/latest
# true
# Check again, the tag doesn't exist in your private registry server

# $ curl -X GET localhost:5000/v1/repositories/ubuntu/tags/latest
# {"error": "Tag not found"}
# curl 192.168.157.154:5000/v1/search
#############################
