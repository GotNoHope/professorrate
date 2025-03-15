from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token 
from .views import api_root, RegisterView, ModuleListView, ProfessorListView, ProfessorRatingView, RateProfessorView, LogoutView

urlpatterns = [
    path('', api_root, name='api-root'),  # API root
    path('register/', RegisterView.as_view(), name='api-register'),
    path('modules/', ModuleListView.as_view(), name='modules-list'),
    path('professors/', ProfessorListView.as_view(), name='professors-list'),
    path('ratings/<int:professor_id>/<str:module_code>/', ProfessorRatingView.as_view(), name='professor-rating'),
    path('rate/', RateProfessorView.as_view(), name='rate-professor'),
    
    # authentication endpoints
    path('login/', obtain_auth_token, name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
]