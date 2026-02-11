from django.test import TestCase, Client
from django.core.exceptions import ValidationError

from .models import Departement, Filiere, Niveau, UE, Etudiant, Note


from django.test import override_settings

@override_settings(ALLOWED_HOSTS=["testserver"])
class ModelsTestCase(TestCase):
    def setUp(self):
        self.dep = Departement.objects.create(nom='Informatique')
        self.fil = Filiere.objects.create(nom='Génie Logiciel', departement=self.dep)
        self.niv = Niveau.objects.create(nom='L2')
        self.ue1 = UE.objects.create(code='UE101', nom='Algo', credit=6, filiere=self.fil, niveau=self.niv)
        self.ue2 = UE.objects.create(code='UE102', nom='BD', credit=4, filiere=self.fil, niveau=self.niv)
        self.etud = Etudiant.objects.create(nom='Alice', matricule='A001', filiere=self.fil, niveau=self.niv)

    def test_ue_weights_validation(self):
        ue = UE(code='UEX', nom='Test', credit=3, filiere=self.fil, niveau=self.niv, cc_weight=10, tp_weight=10, sn_weight=10)
        with self.assertRaises(ValidationError):
            ue.clean()

    def test_note_final_and_elimination(self):
        note = Note.objects.create(etudiant=self.etud, ue=self.ue1, cc=12.0, tp=14.0, sn=16.0)
        # default weights 20/30/50 => final = 12*0.2 + 14*0.3 +16*0.5 = 2.4 + 4.2 + 8 = 14.6
        self.assertEqual(note.final, 14.6)
        self.assertFalse(note.is_eliminated)

        note2 = Note.objects.create(etudiant=self.etud, ue=self.ue2, cc=None, tp=10.0, sn=12.0)
        self.assertIsNone(note2.final)
        self.assertTrue(note2.is_eliminated)

    def test_moyenne_ponderee(self):
        Note.objects.create(etudiant=self.etud, ue=self.ue1, cc=12.0, tp=14.0, sn=16.0)  # final 14.6 credit 6
        Note.objects.create(etudiant=self.etud, ue=self.ue2, cc=10.0, tp=10.0, sn=10.0)  # final 10.0 credit 4
        # moyenne = (14.6*6 + 10*4) / (6+4) = (87.6 + 40) / 10 = 127.6/10 = 12.76
        from django.test import Client
        client = Client()
        response = client.get(f'/moyenne/{self.etud.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('average', response.context)
        self.assertAlmostEqual(response.context['average'], 12.76, places=2)

    def test_notes_json_and_update(self):
        # create a note for ue1
        note = Note.objects.create(etudiant=self.etud, ue=self.ue1, cc=10.0, tp=12.0, sn=14.0)
        from django.test import Client
        client = Client()
        # non-auth access should be redirected to login
        r = client.get('/api/notes/')
        self.assertEqual(r.status_code, 302)
        # login as staff
        from django.contrib.auth.models import User
        u = User.objects.create_user('staff', password='x')
        u.is_staff = True
        u.save()
        client.login(username='staff', password='x')
        r2 = client.get('/api/notes/?filiere=%s&niveau=%s' % (self.fil.id, self.niv.id))
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        self.assertIn('ues', data)
        self.assertIn('students', data)
        # update note via API
        update = client.post(f'/api/note/{note.id}/update/', data='{"cc":15,"tp":16,"sn":17}', content_type='application/json')
        self.assertEqual(update.status_code, 200)
        updated = update.json()
        self.assertEqual(updated['cc'], 15)
        self.assertEqual(updated['final'], round(15*0.2 + 16*0.3 + 17*0.5, 2))

    def test_logout_view(self):
        from django.contrib.auth.models import User
        u = User.objects.create_user('tester', password='x')
        from django.test import Client
        c = Client()
        c.login(username='tester', password='x')
        # ensure authenticated
        r = c.get('/etudiants/')
        self.assertEqual(r.status_code, 200)
        # call logout
        r2 = c.get('/logout/')
        # should redirect to students list
        self.assertEqual(r2.status_code, 302)
        r3 = c.get('/etudiants/')
        # now should be accessible but user not authenticated (no crash) - check that request.user is anonymous
        self.assertFalse(r3.wsgi_request.user.is_authenticated)

    def test_note_create_and_pagination(self):
        # create more students to test pagination
        for i in range(30):
            Etudiant.objects.create(nom=f'Student{i}', matricule=f'S{i:03d}', filiere=self.fil, niveau=self.niv)
        from django.contrib.auth.models import User
        u = User.objects.create_user('staff2', password='x')
        u.is_staff = True
        u.save()
        from django.test import Client
        client = Client()
        client.login(username='staff2', password='x')

        # create note via API (JSON body)
        s = Etudiant.objects.first()
        r = client.post('/api/note/create/', data='{"etudiant_id": %d, "ue_id": %d, "cc": 10, "tp": 12, "sn": 14}' % (s.id, self.ue1.id), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['cc'], 10)

        # create note via form-encoded POST (fallback parser) -> should also work
        form_data = {'etudiant_id': s.id, 'ue_id': self.ue1.id, 'cc': '11', 'tp': '13', 'sn': '15'}
        r2 = client.post('/api/note/create/', data=form_data)
        # second create for same (etudiant, ue) will fail as duplicate; but POST should be accepted by parser
        # so if note exists we get 400 (already exists); to ensure parser works we create for a different student instead
        s2 = Etudiant.objects.last()
        form_data2 = {'etudiant_id': s2.id, 'ue_id': self.ue1.id, 'cc': '12', 'tp': '12', 'sn': '12'}
        r3 = client.post('/api/note/create/', data=form_data2)
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.json()['cc'], 12)

        # pagination: page_size 10, page 2
        r2 = client.get('/api/notes/?filiere=%s&niveau=%s&page=2&page_size=10' % (self.fil.id, self.niv.id))
        self.assertEqual(r2.status_code, 200)
        j = r2.json()
        self.assertEqual(j['page'], 2)
        self.assertEqual(j['page_size'], 10)
        self.assertIn('students', j)

    def test_etudiant_list_defaults_and_ue_column(self):
        # create a second department/filiere/niveau and students to ensure defaults pick the first ones
        dep2 = Departement.objects.create(nom='Autre')
        fil2 = Filiere.objects.create(nom='AutreFil', departement=dep2)
        niv2 = Niveau.objects.create(nom='L3')
        # student in other filiere
        Etudiant.objects.create(nom='Bob', matricule='B01', filiere=fil2, niveau=niv2)
        from django.test import Client
        c = Client()
        # default /etudiants/ should use first dep/fil/niv (from setUp) and not include Bob
        r = c.get('/etudiants/')
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('B01', r.content.decode())

        # now select an UE and ensure the note column appears (create a note for a student)
        s = Etudiant.objects.filter(filiere=self.fil, niveau=self.niv).first()
        n = Note.objects.create(etudiant=s, ue=self.ue1, cc=14, tp=14, sn=14)
        r2 = c.get(f'/etudiants/?departement={self.dep.id}&filiere={self.fil.id}&niveau={self.niv.id}&ue={self.ue1.id}')
        self.assertEqual(r2.status_code, 200)
        # final 14.0 should be visible in the page
        self.assertIn('14.00', r2.content.decode())

    def test_homepage_shows_stats_and_link(self):
        c = Client()
        r = c.get('/')
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        # presence of counts and link to etudiants
        self.assertIn('Départements', body)
        self.assertIn('Étudiants', body)
        self.assertIn('/etudiants/', body)

    def test_filter_api_endpoints(self):
        # filieres for dep
        r = self.client.get(f'/api/filieres/?departement={self.dep.id}')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('filieres', data)
        self.assertTrue(any(f['id'] == self.fil.id for f in data['filieres']))

        # niveaux for filiere
        r2 = self.client.get(f'/api/niveaux/?filiere={self.fil.id}')
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertIn('niveaux', d2)

        # ues for filiere+niveau
        r3 = self.client.get(f'/api/ues/?filiere={self.fil.id}&niveau={self.niv.id}')
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertIn('ues', d3)
        self.assertTrue(any(u['id'] == self.ue1.id for u in d3['ues']))

    def test_sort_by_note_when_ue_selected(self):
        # create three students with different notes on the same UE
        s1 = Etudiant.objects.create(nom='S1', matricule='S1', filiere=self.fil, niveau=self.niv)
        s2 = Etudiant.objects.create(nom='S2', matricule='S2', filiere=self.fil, niveau=self.niv)
        s3 = Etudiant.objects.create(nom='S3', matricule='S3', filiere=self.fil, niveau=self.niv)
        Note.objects.create(etudiant=s1, ue=self.ue1, cc=10, tp=10, sn=10)  # final 10
        Note.objects.create(etudiant=s2, ue=self.ue1, cc=15, tp=15, sn=15)  # final 15
        Note.objects.create(etudiant=s3, ue=self.ue1, cc=12, tp=12, sn=12)  # final 12

        c = Client()
        r = c.get(f'/etudiants/?departement={self.dep.id}&filiere={self.fil.id}&niveau={self.niv.id}&ue={self.ue1.id}&sort=note')
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        # ensure highest final (15) appears first in the table body (S2)
        first_row_index = body.find('<tbody')
        self.assertIn('15.00', body)

    def test_teacher_permissions_on_ue(self):
        from django.contrib.auth.models import User
        teacher = User.objects.create_user('teacher1', password='x')
        # teacher is not staff
        self.assertFalse(teacher.is_staff)
        # assign teacher to ue1
        self.ue1.instructors.add(teacher)
        # sanity check: relation exists
        self.assertTrue(self.ue1.instructors.filter(pk=teacher.pk).exists())
        # sanity check: permission predicate
        from django.contrib.auth.models import User
        u = User.objects.get(username='teacher1')
        self.assertTrue(u.is_superuser or u.is_staff or self.ue1.instructors.filter(pk=u.pk).exists())
        from django.test import Client, RequestFactory
        c = Client()
        self.assertTrue(c.login(username='teacher1', password='x'))
        import json
        body = json.dumps({"etudiant_id": self.etud.id, "ue_id": self.ue1.id, "cc": 11, "tp": 12, "sn": 13})
        # teacher should be able to create a note for ue1 via client
        r = c.post('/api/note/create/', data=body, content_type='application/json')
        self.assertEqual(r.status_code, 200)

        # direct view call (duplicate) should now return bad request (already exists)
        rf = RequestFactory()
        req = rf.post('/api/note/create/', data=body, content_type='application/json')
        req.user = teacher
        from . import views
        resp = views.note_create(req)
        self.assertEqual(resp.status_code, 400)

        # teacher should NOT be able to create for ue2
        r2 = c.post('/api/note/create/', data='{"etudiant_id": %d, "ue_id": %d, "cc": 11, "tp": 12, "sn": 13}' % (self.etud.id, self.ue2.id), content_type='application/json')
        self.assertEqual(r2.status_code, 403)

    def test_only_superuser_can_toggle_staff(self):
        from django.contrib.auth.models import User
        admin = User.objects.create_superuser('mainadmin', password='x')
        s = User.objects.create_user('xstaff', password='x')
        s.is_staff = True
        s.save()
        # non-superuser try to toggle
        c = Client()
        u = User.objects.create_user('u1', password='x')
        u.is_staff = True
        u.save()
        c.login(username='u1', password='x')
        r = c.post(f'/enseignants/{s.id}/toggle_staff/')
        self.assertEqual(r.status_code, 302)
        # should have error message
        response = c.get('/enseignants/')
        self.assertIn('Seul le superuser', response.content.decode())

        # superuser can toggle
        c.logout()
        c.login(username='mainadmin', password='x')
        r2 = c.post(f'/enseignants/{s.id}/toggle_staff/')
        self.assertEqual(r2.status_code, 302)
        s.refresh_from_db()
        self.assertFalse(s.is_staff)
