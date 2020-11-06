from django.contrib import admin
from django.urls import include, path
from virtual_wallet import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/init/', views.Initialize.as_view()),
    # path('api/v1/wallet/', include('walletapp.urls'))     
]
