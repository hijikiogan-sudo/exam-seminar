/* Progressive enhancement: without JavaScript all subjects remain readable. */
(() => {
  const subjects = [...document.querySelectorAll('[data-subject]')];
  const nav = [...document.querySelectorAll('[data-subject-link]')];
  const variants = [...document.querySelectorAll('[data-variant]')];
  const variantLinks = [...document.querySelectorAll('[data-variant-link]')];
  let printing = false;
  function select() {
    if (!subjects.length || printing) return;
    const parts = location.hash.slice(1).split('/');
    const key = subjects.some(x => x.dataset.subject === parts[0]) ? parts[0] : 'japanese';
    const variant = parts[1] === 'practice' ? 'practice' : 'summary';
    subjects.forEach(x => x.hidden = x.dataset.subject !== key);
    nav.forEach(x => x.setAttribute('aria-current', String(x.dataset.subjectLink === key)));
    variants.forEach(x => x.hidden = x.dataset.variant !== variant);
    variantLinks.forEach(x => x.setAttribute('aria-current', String(x.dataset.variantLink === variant)));
    document.title = document.querySelector(`[data-subject="${key}"] h2`).textContent + '｜' + document.body.dataset.date + ' 入試実戦オンラインゼミ';
  }
  nav.concat(variantLinks).forEach(x => x.addEventListener('click', () => requestAnimationFrame(() => {
    select();
    document.querySelector('.subject-nav')?.scrollIntoView({block:'start'});
  })));
  addEventListener('hashchange', select);
  let closed = [];
  addEventListener('beforeprint', () => {
    printing = true;
    subjects.concat(variants).forEach(x => x.hidden = false);
    closed = [...document.querySelectorAll('details:not([open])')];
    closed.forEach(x => x.open = true);
  });
  addEventListener('afterprint', () => { closed.forEach(x => x.open = false); printing = false; select(); });
  document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
  const search = document.querySelector('[data-search]');
  search?.addEventListener('input', () => {
    let n = 0;
    document.querySelectorAll('[data-session]').forEach(x => { x.hidden = !x.textContent.toLowerCase().includes(search.value.trim().toLowerCase()); if(!x.hidden)n++; });
    document.querySelector('[data-count]').textContent = `${n}回`;
    document.querySelector('[data-no-results]').hidden = n !== 0;
  });
  select();
})();
