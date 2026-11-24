/** Article enhancements: citation preview cards and glossary-card positioning / Esc dismissal. */

// ---- Citation previews (C7): clone the matching References item into a floating card.
let card: HTMLDivElement | null = null;
let hideTimer: number | undefined;

function getCard() {
  if (!card) {
    card = document.createElement('div');
    card.className = 'cite-preview';
    card.setAttribute('role', 'tooltip');
    card.id = 'cite-preview';
    card.addEventListener('mouseenter', () => window.clearTimeout(hideTimer));
    card.addEventListener('mouseleave', scheduleHide);
    document.body.appendChild(card);
  }
  return card;
}
function scheduleHide() {
  window.clearTimeout(hideTimer);
  hideTimer = window.setTimeout(() => card?.classList.remove('is-open'), 150);
}
function showFor(link: HTMLAnchorElement) {
  const ref = document.querySelector<HTMLElement>(link.getAttribute('href')!);
  if (!ref) return;
  window.clearTimeout(hideTimer);
  const c = getCard();
  const num = link.textContent?.replace(/[[\]]/g, '') ?? '';
  const body = ref.querySelector('.ref__body');
  c.innerHTML = `<span class="cite-preview__num">Reference ${num}</span>${body ? body.innerHTML : ref.innerHTML}`;
  const r = link.getBoundingClientRect();
  const width = 340;
  let left = window.scrollX + r.left + r.width / 2 - width / 2;
  left = Math.max(window.scrollX + 16, Math.min(left, window.scrollX + document.documentElement.clientWidth - width - 16));
  c.style.left = `${left}px`;
  c.classList.add('is-open');
  const h = c.offsetHeight;
  const below = r.bottom + 10 + h < window.innerHeight;
  c.style.top = `${window.scrollY + (below ? r.bottom + 10 : r.top - h - 10)}px`;
  link.setAttribute('aria-describedby', 'cite-preview');
}

document.addEventListener('mouseover', (e) => {
  const a = (e.target as HTMLElement).closest<HTMLAnchorElement>('[data-cite-link]');
  if (a) showFor(a);
});
document.addEventListener('mouseout', (e) => {
  if ((e.target as HTMLElement).closest('[data-cite-link]')) scheduleHide();
});
document.addEventListener('focusin', (e) => {
  const a = (e.target as HTMLElement).closest<HTMLAnchorElement>('[data-cite-link]');
  if (a) showFor(a);
  else if (!(e.target as HTMLElement).closest('.cite-preview')) card?.classList.remove('is-open');
});
document.addEventListener('click', (e) => {
  if ((e.target as HTMLElement).closest('[data-cite-link]')) card?.classList.remove('is-open');
});

// ---- Glossary cards (C8): flip above when there is no room below; Esc dismisses.
document.addEventListener('mouseover', (e) => {
  const t = (e.target as HTMLElement).closest<HTMLElement>('[data-term]');
  if (!t) return;
  t.classList.remove('dismissed');
  const r = t.getBoundingClientRect();
  t.classList.toggle('flip', window.innerHeight - r.bottom < 220);
});
document.addEventListener('focusin', (e) => {
  const t = (e.target as HTMLElement).closest<HTMLElement>('[data-term]');
  if (t) {
    t.classList.remove('dismissed');
    t.classList.toggle('flip', window.innerHeight - t.getBoundingClientRect().bottom < 220);
  }
});
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  document.querySelectorAll('[data-term]').forEach((t) => t.classList.add('dismissed'));
  card?.classList.remove('is-open');
});
