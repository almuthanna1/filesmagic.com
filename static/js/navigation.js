document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('nav');
    let lastScrollTop = 0;
    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const currentScroll = window.pageYOffset || document.documentElement.scrollTop;

                if (currentScroll > lastScrollTop && currentScroll > 80) {
                    navbar.classList.add('navbar-hidden');
                } else {
                    navbar.classList.remove('navbar-hidden');
                }

                lastScrollTop = Math.max(currentScroll, 0);
                ticking = false;
            });
            ticking = true;
        }
    });
});