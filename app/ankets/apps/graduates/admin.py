from django.contrib import admin
from .models import Respondent, Question, Answer, Result, Links, Raw

# Register your models here.
admin.site.register(Respondent)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Links)
admin.site.register(Raw)
#admin.site.register(Result)