// Basic DataTables-driven table + AJAX editing

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let currentEdit = {note_id: null, ue_id: null, row: null};

function buildTable(ues, students) {
    const thead = document.getElementById('grades-thead');
    if (!thead) return;
    const tr = thead.querySelector('tr');
    if (!tr) return;
    // remove existing UE headers
    while (tr.children.length > 2) tr.removeChild(tr.lastChild);
    ues.forEach(u => {
        const th = document.createElement('th');
        th.textContent = `${u.nom} (${u.code})`;
        th.dataset.ueId = u.id;
        tr.appendChild(th);
    });

    const tbody = document.querySelector('#grades-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    students.forEach(s => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${s.nom}</td><td>${s.matricule}</td>`;
        row.dataset.studentId = s.id;
        ues.forEach(u => {
            const cell = document.createElement('td');
            const note = s.notes[u.id];
            cell.dataset.ueId = u.id;
            cell.dataset.editable = u.editable ? 'true' : 'false';
            if (note) {
                const final = note.final !== null ? note.final.toFixed(2) : '—';
                cell.innerHTML = `CC:${note.cc ?? '—'}<br>TP:${note.tp ?? '—'}<br>SN:${note.sn ?? '—'}<br><strong>F:${final}</strong>`;
                cell.dataset.noteId = note.note_id;
            } else {
                cell.innerHTML = `<em class="text-danger">N/A</em>`;
                cell.dataset.noteId = '';
            }
            if (u.editable) {
                cell.classList.add('note-cell');
                cell.title = 'Cliquez pour modifier';
            } else {
                cell.classList.add('text-muted');
                cell.title = 'Lecture seule';
            }
            row.appendChild(cell);
        });
        tbody.appendChild(row);
    });

    // click handler for editing
    document.querySelectorAll('.note-cell').forEach(cell => {
        cell.addEventListener('click', (e) => {
            if (cell.dataset.editable !== 'true') return;
            const noteId = cell.dataset.noteId;
            currentEdit.note_id = noteId || null;
            currentEdit.ue_id = cell.dataset.ueId;
            currentEdit.row = cell.parentElement;
            // populate modal with existing values
            if (noteId) {
                const parts = cell.innerHTML.split('<br>');
                const cc = parts[0].replace(/[^0-9.\-]/g, '') || '';
                const tp = parts[1].replace(/[^0-9.\-]/g, '') || '';
                const sn = parts[2].replace(/[^0-9.\-]/g, '') || '';
                document.querySelector('#editForm [name=cc]').value = cc;
                document.querySelector('#editForm [name=tp]').value = tp;
                document.querySelector('#editForm [name=sn]').value = sn;
            } else {
                document.querySelector('#editForm [name=cc]').value = '';
                document.querySelector('#editForm [name=tp]').value = '';
                document.querySelector('#editForm [name=sn]').value = '';
            }
            var myModal = new bootstrap.Modal(document.getElementById('editModal'));
            myModal.show();
        });
    });
}

let currentPage = 1;
let pageSize = 25;

function updateImportExportButtons() {
    const niv = document.getElementById('filter-niveau').value;
    const exportBtn = document.getElementById('export-notes-btn');
    const importBtn = document.getElementById('import-notes-btn');
    
    if (niv) {
        exportBtn.disabled = false;
        importBtn.disabled = false;
    } else {
        exportBtn.disabled = true;
        importBtn.disabled = true;
    }
}

function fetchAndRender(page = 1) {
    if (page && typeof page === 'object') {
        page = 1;
    }
    currentPage = page;
    const dep = document.getElementById('filter-departement').value;
    const fil = document.getElementById('filter-filiere').value;
    const niv = document.getElementById('filter-niveau').value;
    const url = new URL(window.location.origin + '/api/notes/');
    if (dep) url.searchParams.append('departement', dep);
    if (fil) url.searchParams.append('filiere', fil);
    if (niv) url.searchParams.append('niveau', niv);
    url.searchParams.append('page', String(currentPage));
    url.searchParams.append('page_size', String(pageSize));

    fetch(url)
        .then(r => r.json())
        .then(data => {
            // convert ues list to map-friendly id strings
            const ues = data.ues.map(u => ({id: u.id, code: u.code, nom: u.nom, credit: u.credit}));
            // transform students notes keys to integers for easier access
            const students = data.students.map(s => {
                const notes = {};
                for (const k in s.notes) {
                    notes[parseInt(k, 10)] = s.notes[k];
                }
                return {...s, notes};
            });
            buildTable(ues, students);

            // pagination UI
            const total = data.total_students;
            const totalPages = Math.max(1, Math.ceil(total / pageSize));
            document.getElementById('page-info').textContent = `Page ${currentPage} / ${totalPages}`;
            document.getElementById('prev-page').classList.toggle('disabled', currentPage <= 1);
            document.getElementById('next-page').classList.toggle('disabled', currentPage >= totalPages);
            
            // Update import/export button states
            updateImportExportButtons();
        });
}

// pagination controls
document.addEventListener('DOMContentLoaded', () => {
    // Cascading filters: department -> filiere -> niveau
    document.getElementById('filter-departement').addEventListener('change', async (event) => {
        const depId = event.target.value;
        const filSelect = document.getElementById('filter-filiere');
        
        filSelect.innerHTML = '<option value="">-- Tous --</option>';
        filSelect.disabled = false;
        
        if (!depId) {
            // If no department selected, disable filière and niveau
            document.getElementById('filter-niveau').innerHTML = '<option value="">-- Tous --</option>';
            document.getElementById('filter-niveau').disabled = true;
            return;
        }
        
        // Fetch filieres for selected department
        try {
            const response = await fetch(`/api/filieres/?departement=${depId}`);
            const data = await response.json();
            data.filieres.forEach(f => {
                const opt = document.createElement('option');
                opt.value = f.id;
                opt.textContent = f.nom;
                filSelect.appendChild(opt);
            });
        } catch (err) {
            console.error('Error fetching filieres:', err);
        }
        
        // Reset niveau when department changes
        document.getElementById('filter-niveau').innerHTML = '<option value="">-- Tous --</option>';
        document.getElementById('filter-niveau').disabled = true;
    });
    
    document.getElementById('filter-filiere').addEventListener('change', async (event) => {
        const filId = event.target.value;
        const nivSelect = document.getElementById('filter-niveau');
        
        nivSelect.innerHTML = '<option value="">-- Sélectionnez un niveau --</option>';
        nivSelect.disabled = true;
        
        if (!filId) {
            nivSelect.disabled = true;
            updateImportExportButtons();
            return;
        }
        
        // Fetch niveaux for selected filiere
        try {
            const response = await fetch(`/api/niveaux/?filiere=${filId}`);
            const data = await response.json();
            nivSelect.disabled = false;
            data.niveaux.forEach(n => {
                const opt = document.createElement('option');
                opt.value = n.id;
                opt.textContent = n.nom;
                nivSelect.appendChild(opt);
            });
        } catch (err) {
            console.error('Error fetching niveaux:', err);
        }
        
        // Update button state
        updateImportExportButtons();
        
        // Trigger table update when filiere changes
        fetchAndRender(1);
    });
    
    document.getElementById('filter-niveau').addEventListener('change', () => {
        updateImportExportButtons();
        fetchAndRender(1);
    });

    document.getElementById('prev-page').addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage > 1) fetchAndRender(currentPage - 1);
    });
    document.getElementById('next-page').addEventListener('click', (e) => {
        e.preventDefault();
        // we don't know totalPages here but server will clamp
        fetchAndRender(currentPage + 1);
    });

    // save edit
    const applyBtn = document.getElementById('apply-filters');
    if (applyBtn) {
        applyBtn.addEventListener('click', () => fetchAndRender(1));
    }

    document.getElementById('saveEdit').addEventListener('click', () => {
        const ccRaw = document.querySelector('#editForm [name=cc]').value;
        const tpRaw = document.querySelector('#editForm [name=tp]').value;
        const snRaw = document.querySelector('#editForm [name=sn]').value;
        const cc = ccRaw === '' ? null : parseFloat(ccRaw);
        const tp = tpRaw === '' ? null : parseFloat(tpRaw);
        const sn = snRaw === '' ? null : parseFloat(snRaw);

        if (!currentEdit.note_id) {
            // create new note via API
            const etudiantId = currentEdit.row.dataset.studentId;
            fetch(`/api/note/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({etudiant_id: etudiantId, ue_id: currentEdit.ue_id, cc, tp, sn})
            }).then(r => {
                if (!r.ok) return r.text().then(t => { throw new Error(t) });
                return r.json();
            }).then(data => {
                // update cell with created note
                const cell = currentEdit.row.querySelector(`td[data-ue-id="${currentEdit.ue_id}"]`);
                const final = data.final !== null ? data.final.toFixed(2) : '—';
                cell.dataset.noteId = data.id;
                cell.innerHTML = `CC:${data.cc ?? '—'}<br>TP:${data.tp ?? '—'}<br>SN:${data.sn ?? '—'}<br><strong>F:${final}</strong>`;
                var myModalEl = document.getElementById('editModal')
                var modal = bootstrap.Modal.getInstance(myModalEl)
                modal.hide();
            }).catch(err => {
                alert('Erreur lors de la création: ' + err.message);
            });
            return;
        }

        fetch(`/api/note/${currentEdit.note_id}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({cc, tp, sn})
        }).then(r => {
            if (!r.ok) throw new Error('Erreur sauvegarde');
            return r.json();
        }).then(data => {
            // update current cell content
            const cell = currentEdit.row.querySelector(`td[data-ue-id="${currentEdit.ue_id}"]`);
            const final = data.final !== null ? data.final.toFixed(2) : '—';
            cell.innerHTML = `CC:${data.cc ?? '—'}<br>TP:${data.tp ?? '—'}<br>SN:${data.sn ?? '—'}<br><strong>F:${final}</strong>`;
            var myModalEl = document.getElementById('editModal')
            var modal = bootstrap.Modal.getInstance(myModalEl)
            modal.hide();
        }).catch(err => {
            alert('Erreur lors de la sauvegarde: ' + err.message);
        });
    });

    // Export notes
    document.getElementById('export-notes-btn').addEventListener('click', () => {
        const fil = document.getElementById('filter-filiere').value;
        const niv = document.getElementById('filter-niveau').value;
        if (!fil || !niv) {
            alert('Veuillez sélectionner une filière et un niveau');
            return;
        }
        // Build export URL with current filters
        const url = new URL(window.location.origin + '/api/notes/export/');
        url.searchParams.append('filiere_id', fil);
        url.searchParams.append('niveau_id', niv);
        window.location.href = url.toString();
    });

    // Import notes
    document.getElementById('import-notes-btn').addEventListener('click', () => {
        const uesSelect = document.getElementById('import-ue');
        // Populate UE dropdown from current table
        const ueHeaders = document.querySelectorAll('#grades-thead th');
        uesSelect.innerHTML = '<option value="">-- Sélectionnez une UE --</option>';
        ueHeaders.forEach((th, idx) => {
            if (idx > 1) { // Skip nom and matricule columns
                const ueId = th.dataset.ueId;
                const text = th.textContent.trim();
                if (ueId) {
                    const opt = document.createElement('option');
                    opt.value = ueId;
                    opt.textContent = text;
                    uesSelect.appendChild(opt);
                }
            }
        });
        const importModal = new bootstrap.Modal(document.getElementById('importModal'));
        importModal.show();
    });

    document.getElementById('doImport').addEventListener('click', () => {
        const ueId = document.getElementById('import-ue').value;
        const fileInput = document.getElementById('import-file');
        const file = fileInput.files[0];
        if (!ueId || !file) {
            alert('Veuillez sélectionner une UE et un fichier');
            return;
        }
        const formData = new FormData();
        formData.append('ue_id', ueId);
        formData.append('file', file);
        document.getElementById('import-progress').style.display = 'block';
        document.getElementById('import-status').textContent = 'Importation en cours...';
        fetch('/api/notes/import/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        }).then(r => r.json()).then(data => {
            if (data.success) {
                document.getElementById('import-status').textContent = `✓ ${data.imported} créés, ${data.updated} mis à jour`;
                if (data.errors.length > 0) {
                    alert('Avertissements:\n' + data.errors.slice(0, 5).join('\n'));
                }
                setTimeout(() => {
                    document.getElementById('import-progress').style.display = 'none';
                    fileInput.value = '';
                    var myModalEl = document.getElementById('importModal');
                    var modal = bootstrap.Modal.getInstance(myModalEl);
                    modal.hide();
                    fetchAndRender(1);
                }, 1000);
            } else {
                alert('Erreur: ' + data.error);
                document.getElementById('import-progress').style.display = 'none';
            }
        }).catch(err => {
            alert('Erreur réseau: ' + err.message);
            document.getElementById('import-progress').style.display = 'none';
        });
    });

    // initial load
    updateImportExportButtons();
    fetchAndRender();
});