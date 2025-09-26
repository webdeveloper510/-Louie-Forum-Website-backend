from django.contrib import admin
from . models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Answer)
admin.site.register(Post)
admin.site.register(Comment)