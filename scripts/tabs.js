// Tabs script: classify cards, update counts, and filter
(function(){
  const tablist = document.querySelector('.tabs');
  const grid = document.querySelector('.grid');
  if (!tablist || !grid) return;
  const tabs = Array.from(tablist.querySelectorAll('[role=tab]'));
  const cards = Array.from(grid.querySelectorAll('.card'));

  function classify(card){
    const title = (card.querySelector('.title')||{textContent:''}).textContent.trim();
    if (/^M\s*\d+/i.test(title) || /^M\d+/i.test(title)) return 'messier';
    if (/^NGC\s*\d+/i.test(title)) return 'ngc';
    return 'other';
  }

  cards.forEach(c=> c.setAttribute('data-catalog', classify(c)));

  function counts(){
    const all = cards.length;
    const messier = cards.filter(c=> c.getAttribute('data-catalog')==='messier').length;
    const ngc = cards.filter(c=> c.getAttribute('data-catalog')==='ngc').length;
    return {all,messier,ngc};
  }

  function updateTabLabels(){
    const c = counts();
    tabs.forEach(t=>{
      const filter = t.getAttribute('data-filter');
      if (filter === 'all') t.textContent = `All (${c.all})`;
      if (filter === 'messier') t.textContent = `Messier (${c.messier})`;
      if (filter === 'ngc') t.textContent = `NGC (${c.ngc})`;
    });
  }

  function selectFilter(filter){
    tabs.forEach(t=> t.setAttribute('aria-selected', t.getAttribute('data-filter')===filter ? 'true' : 'false'));
    cards.forEach(c=> c.classList.toggle('hidden', filter !== 'all' && c.getAttribute('data-catalog') !== filter));
  }

  tablist.addEventListener('click', (e)=>{
    const btn = e.target.closest('[role=tab]');
    if (!btn) return;
    const filter = btn.getAttribute('data-filter');
    selectFilter(filter);
  });
  tablist.addEventListener('keydown', (e)=>{
    const active = tablist.querySelector('[role=tab][aria-selected="true"]');
    let idx = tabs.indexOf(active);
    if (e.key === 'ArrowRight') idx = (idx+1) % tabs.length;
    if (e.key === 'ArrowLeft') idx = (idx-1+tabs.length) % tabs.length;
    const next = tabs[idx]; if (next) { next.focus(); next.click(); }
  });

  updateTabLabels();
})();
