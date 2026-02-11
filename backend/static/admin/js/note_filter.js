(function() {
  'use strict';
  
  // Wait for Django admin to be ready
  document.addEventListener('DOMContentLoaded', function() {
    const etudiantSelect = document.getElementById('id_etudiant');
    const ueSelect = document.getElementById('id_ue');
    
    if (!etudiantSelect || !ueSelect) {
      return;
    }
    
    // Store the original UE options
    const originalOptions = Array.from(ueSelect.options).map(opt => ({
      value: opt.value,
      text: opt.text,
      selected: opt.selected
    }));
    
    // Function to filter UE options based on selected Etudiant
    function filterUEOptions() {
      const etudiantId = etudiantSelect.value;
      
      if (!etudiantId) {
        // Show all UEs if no etudiant selected
        ueSelect.innerHTML = '';
        originalOptions.forEach(opt => {
          const option = document.createElement('option');
          option.value = opt.value;
          option.text = opt.text;
          option.selected = opt.selected;
          ueSelect.appendChild(option);
        });
        return;
      }
      
      // Fetch filtered UEs for this etudiant
      fetch(`/api/etudiant_ues/?etudiant=${etudiantId}`)
        .then(response => response.json())
        .then(data => {
          const filteredUeIds = data.map(ue => ue.id.toString());
          
          ueSelect.innerHTML = '';
          
          // Add empty option if present in original
          const emptyOpt = originalOptions.find(opt => !opt.value);
          if (emptyOpt) {
            const option = document.createElement('option');
            option.value = '';
            option.text = emptyOpt.text;
            ueSelect.appendChild(option);
          }
          
          // Add filtered UEs
          originalOptions.forEach(opt => {
            if (opt.value && filteredUeIds.includes(opt.value)) {
              const option = document.createElement('option');
              option.value = opt.value;
              option.text = opt.text;
              option.selected = opt.selected;
              ueSelect.appendChild(option);
            }
          });
        })
        .catch(error => console.error('Error filtering UEs:', error));
    }
    
    // Attach change listener to etudiant select
    etudiantSelect.addEventListener('change', filterUEOptions);
  });
})();
