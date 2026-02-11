from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('etudiants/', views.etudiant_list, name='etudiants_list'),
    path('etudiants/ajouter/', views.etudiant_create, name='etudiant_add'),

    # tableau dynamique
    path('tableau/', views.tableau_notes, name='tableau_notes'),
    path('api/notes/', views.notes_json, name='notes_json'),
    # cascade filter endpoints
    path('api/filieres/', views.filieres_json, name='filieres_json'),
    path('api/niveaux/', views.niveaux_json, name='niveaux_json'),
    path('api/ues/', views.ues_json, name='ues_json'),
    path('api/etudiant_ues/', views.etudiant_ues_json, name='etudiant_ues_json'),
    path('api/note/<int:note_id>/update/', views.note_update, name='note_update'),
    path('api/note/create/', views.note_create, name='note_create'),
    path('api/notes/import/', views.notes_import_excel, name='notes_import_excel'),
    path('api/notes/export/', views.notes_export_excel, name='notes_export_excel'),

    # enseignants
    path('enseignants/', views.enseignants_list, name='enseignants_list'),
    path('enseignants/ajouter/', views.enseignant_create, name='enseignant_add'),
    path('enseignants/<int:user_id>/toggle_staff/', views.enseignant_toggle_staff, name='enseignant_toggle_staff'),

    path('logout/', views.logout_view, name='logout'),

    path('moyenne/<int:etudiant_id>/', views.moyenne_etudiant, name='moyenne'),
    path('moyenne/<int:etudiant_id>/export/', views.moyenne_etudiant_pdf, name='moyenne_pdf'),
]

