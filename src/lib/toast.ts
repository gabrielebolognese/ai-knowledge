/** Small polite toast (role=status). Uses the #toast-region element rendered by BaseLayout. */
let timer: number | undefined;
export function showToast(message: string, ms = 3000) {
  const region = document.getElementById('toast-region');
  if (!region) return;
  let el = region.querySelector<HTMLElement>('.toast');
  if (!el) {
    el = document.createElement('div');
    el.className = 'toast';
    region.appendChild(el);
  }
  el.textContent = message;
  requestAnimationFrame(() => el!.classList.add('is-visible'));
  window.clearTimeout(timer);
  timer = window.setTimeout(() => el!.classList.remove('is-visible'), ms);
}
