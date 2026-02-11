document.addEventListener('DOMContentLoaded', function() {
  const depSel = document.getElementById('departement-select');
  const filSel = document.getElementById('filiere-select');
  const nivSel = document.getElementById('niveau-select');
  const ueSel = document.getElementById('ue-select');

  function setOptions(select, items, placeholder='--') {
    if (!select) return;
    select.innerHTML = '';
    const opt0 = document.createElement('option'); opt0.value = ''; opt0.textContent = placeholder; select.appendChild(opt0);
    items.forEach(i => {
      const o = document.createElement('option'); o.value = i.id; o.textContent = i.nom || i.code || i.id; select.appendChild(o);
    });
  }

  depSel && depSel.addEventListener('change', function() {
    const dep = this.value;
    fetch(`/api/filieres/?departement=${dep}`)
      .then(r => r.json())
      .then(d => {
        setOptions(filSel, d.filieres);
        // trigger filiere population if available
        const firstFil = filSel.querySelector('option[value]:not([value=""])');
        const filVal = firstFil ? firstFil.value : '';
        if (filVal) {
          filSel.value = filVal;
          filSel.dispatchEvent(new Event('change'));
        } else {
          setOptions(nivSel, []);
          setOptions(ueSel, []);
        }
      })
      .catch(err => console.error('filieres fetch error', err));
  });

  filSel && filSel.addEventListener('change', function() {
    const fil = this.value;
    fetch(`/api/niveaux/?filiere=${fil}`)
      .then(r => r.json())
      .then(d => {
        setOptions(nivSel, d.niveaux);
        const firstNiv = nivSel.querySelector('option[value]:not([value=""])');
        const nivVal = firstNiv ? firstNiv.value : '';
        if (nivVal) {
          nivSel.value = nivVal;
          nivSel.dispatchEvent(new Event('change'));
        } else {
          setOptions(ueSel, []);
        }
      })
      .catch(err => console.error('niveaux fetch error', err));
  });

  nivSel && nivSel.addEventListener('change', function() {
    const fil = filSel ? filSel.value : '';
    const niv = this.value;
    fetch(`/api/ues/?filiere=${fil}&niveau=${niv}`)
      .then(r => r.json())
      .then(d => {
        setOptions(ueSel, d.ues.map(u => ({id: u.id, nom: `${u.code} - ${u.nom}`})));
      })
      .catch(err => console.error('ues fetch error', err));
  });

  // initial population: if selects are empty but have server-selected values, do nothing; otherwise trigger cascade
  if (depSel && depSel.value && filSel && filSel.options.length <= 1) {
    depSel.dispatchEvent(new Event('change'));
  } else if (filSel && filSel.value && nivSel && nivSel.options.length <= 1) {
    filSel.dispatchEvent(new Event('change'));
  }
});