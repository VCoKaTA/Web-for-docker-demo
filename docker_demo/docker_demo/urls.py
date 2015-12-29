from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('demo.views',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'views.index',name='indexurl'),
	url(r'^login/$','views.login',name='loginurl'),
	url(r'^login_auth/$','views.login_auth',name='login_authurl'),
	url(r'^logout/$','views.logout',name='logouturl'),
	url(r'^index/$','views.index', name='dockerindexurl'),
	url(r'^container/list/$','views.container_list', name='listcontainerurl'),
	url(r'^container/create/$','views.container_create', name='createcontainerurl'),
	url(r'^container/delete/(?P<id>\d+)$','views.container_delete', name='deletecontainerurl'),
	url(r'^container/stop/(?P<id>\d+)$','views.container_stop', name='stopcontainerurl'),
	url(r'^container/start/(?P<id>\d+)$','views.container_start', name='startcontainerurl'),
	url(r'^container/restart/(?P<id>\d+)$','views.container_restart', name='restartcontainerurl'),
	url(r'^image/list/$','views.image_list', name='listimageurl'),
	url(r'^image/delete/(?P<id>\d+)/$','views.image_delete', name='deleteimageurl'),
	url(r'^image/build/$','views.image_build', name='buildimageurl'),
	url(r'^image/refresh/$','views.image_refresh', name='refreshimageurl'),
	url(r'^image/dockerfile/$','views.dockerfile', name='dockerfileurl'),
	url(r'^image/commit/(?P<id>\d+)$','views.image_commit', name='commitimageurl'),
	# url(r'^image/pull/$','views.image_pull', name='pullimageurl'),
	# url(r'^image/push/$','views.image_push', name='pushimageurl'),

)
