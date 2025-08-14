(function(){
  const form = document.querySelector('form[data-enhanced="1"]');
  if(!form) return;

  // Live counters for any textarea with maxlength
  function attachCounter(area){
    const max = parseInt(area.getAttribute('maxlength')||'0',10);
    if(!max) return;
    // Look for a sibling .counter in the same .row
    const counter = area.closest('.row')?.querySelector('.counter');
    if(!counter) return;
    function update(){
      const left = Math.max(0, max - (area.value || '').length);
      counter.textContent = left + ' remaining';
    }
    area.addEventListener('input', update);
    update();
  }
  document.querySelectorAll('textarea[maxlength]').forEach(attachCounter);

  // Prevent accidental double submit
  const btn = form.querySelector('button[type="submit"]');
  form.addEventListener('submit', function(){
    if(!form.checkValidity()) return;
    if(btn){ btn.disabled = true; btn.textContent = 'Working…'; }
  });
})();
