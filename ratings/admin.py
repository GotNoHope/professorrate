from django.contrib import admin
from .models import Professor, Module, Rating

admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(Rating)