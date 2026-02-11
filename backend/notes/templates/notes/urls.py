from django.urls import path
from .views import moyenne_etudiant

urlpatterns = [
    path('moyenne/<int:etudiant_id>/', moyenne_etudiant, name='moyenne'),
]
