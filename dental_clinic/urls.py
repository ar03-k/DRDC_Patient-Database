from django.contrib import admin
from django.urls import path, include
from patients import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('add/', views.add_patient, name='add_patient'),
    path('add/success/', views.addpatient_success, name='addpatient_success'),
    path('patients/', views.view_patients, name='view_patients'),
    path('patient/<int:pk>/edit/', views.edit_patient, name='edit_patient'),
    path('patient/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:pk>/add-visit/', views.add_visit, name='add_visit'),
    path('patient/<int:pk>/delete/', views.delete_patient, name='delete_patient'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)