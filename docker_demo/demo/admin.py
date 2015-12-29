from django.contrib import admin
from django.contrib.auth.models import User
from models import *
# Register your models here.
class NodeAdmin(admin.ModelAdmin):
    list_display=('node_ip','node_name','weight','weight_type','node_type','create_image','root_password')
class ImagesAdmin(admin.ModelAdmin):
    list_display=('id','repository','image_id','size','function','node','image_type')
class ContainersAdmin(admin.ModelAdmin):
    list_display=('user','container_name','container_id','container_ip','image','function','status')

admin.site.register(Node, NodeAdmin)
admin.site.register(Images, ImagesAdmin)
admin.site.register(Containers, ContainersAdmin)
