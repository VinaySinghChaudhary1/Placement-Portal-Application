// frontend/src/directives/reveal.js
//
// Lightweight scroll-reveal Vue directive: `v-reveal` (optionally
// `v-reveal="2"` for a staggered delay step 1-4, see motion.css).
//
// Deliberately NOT a third-party animation library — a single
// IntersectionObserver toggling one CSS class keeps the public-page redesign
// dependency-free, so `npm install` never has to run again for this feature
// and there's nothing extra to break across the WSL/Windows-drive dev setup
// this project has already had file-watching issues with this session.

function applyDelay(el, binding) {
  const step = Number(binding.value)
  if (step >= 1 && step <= 4) {
    el.setAttribute('data-reveal-delay', String(step))
  }
}

export default {
  mounted(el, binding) {
    el.classList.add('pp-reveal')
    applyDelay(el, binding)

    // If IntersectionObserver isn't available for some reason, fail open —
    // show the content immediately rather than leaving it invisible forever.
    if (typeof IntersectionObserver === 'undefined') {
      el.classList.add('is-visible')
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            el.classList.add('is-visible')
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.15, rootMargin: '0px 0px -8% 0px' }
    )

    observer.observe(el)
    el._ppRevealObserver = observer
  },
  unmounted(el) {
    if (el._ppRevealObserver) {
      el._ppRevealObserver.disconnect()
      delete el._ppRevealObserver
    }
  }
}
