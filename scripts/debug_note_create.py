from notes.models import Departement,Filiere,Niveau,UE,Etudiant
from django.contrib.auth.models import User
from django.test import Client

# Setup minimal data
dep=Departement.objects.create(nom='D')
fil=Filiere.objects.create(nom='F', departement=dep)
niv=Niveau.objects.create(nom='N')
ue1=UE.objects.create(code='T1',nom='Test',credit=3,filiere=fil,niveau=niv)
ue2=UE.objects.create(code='T2',nom='Test2',credit=3,filiere=fil,niveau=niv)
et=Etudiant.objects.create(nom='E',matricule='M1',filiere=fil,niveau=niv)
teacher=User.objects.create_user('teacher1',password='x')
ue1.instructors.add(teacher)

c=Client()
logged = c.login(username='teacher1', password='x')
print('logged in?', logged)
import json
body=json.dumps({"etudiant_id": et.id, "ue_id": ue1.id, "cc":11, "tp":12, "sn":13})
r=c.post('/api/note/create/', data=body, content_type='application/json')
print('STATUS', r.status_code)
print('CONTENT', r.content)
print('BODY SENT repr:', repr(body))
print('REQUEST.POST:', r.wsgi_request.POST if hasattr(r, 'wsgi_request') else 'no wsgi_request')
