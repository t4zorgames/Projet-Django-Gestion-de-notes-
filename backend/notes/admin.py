from django.contrib import admin
from django.forms import ModelChoiceField
from .models import Departement, Filiere, Niveau, UE, Etudiant, Note


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ('nom',)


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'departement')
    list_filter = ('departement',)


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('nom',)


@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'credit', 'filiere', 'niveau', 'semester', 'cc_weight', 'tp_weight', 'sn_weight')
    list_filter = ('filiere', 'niveau', 'semester')
    search_fields = ('code', 'nom')
    filter_horizontal = ('instructors',)
    # show instructors in change view
    fields = ('code', 'nom', 'credit', 'filiere', 'niveau', 'semester', 'instructors', 'cc_weight', 'tp_weight', 'sn_weight')


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'matricule', 'filiere', 'niveau')
    search_fields = ('nom', 'matricule')
    list_filter = ('filiere', 'niveau')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'ue', 'final_display', 'is_eliminated')
    list_filter = ('ue', 'etudiant__filiere')
    search_fields = ('etudiant__nom', 'etudiant__matricule')

    def final_display(self, obj):
        return obj.final
    final_display.short_description = 'Final'

    def is_eliminated(self, obj):
        return obj.is_eliminated
    is_eliminated.boolean = True
    is_eliminated.short_description = 'Éliminé'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filter UE options based on selected Etudiant's filiere and niveau
        if db_field.name == 'ue':
            # Get the etudiant_id from the request if available (POST or GET)
            etudiant_id = request.POST.get('etudiant') or request.GET.get('etudiant')
            if etudiant_id:
                try:
                    etudiant = Etudiant.objects.get(pk=etudiant_id)
                    # Filter UEs to only those matching the etudiant's filiere and niveau
                    kwargs['queryset'] = UE.objects.filter(
                        filiere=etudiant.filiere,
                        niveau=etudiant.niveau
                    )
                except (Etudiant.DoesNotExist, ValueError):
                    # If etudiant not found or invalid, show all UEs
                    kwargs['queryset'] = UE.objects.all()
            else:
                # If no etudiant selected yet, show all UEs (will be filtered by JS)
                kwargs['queryset'] = UE.objects.all()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/note_filter.js',)
