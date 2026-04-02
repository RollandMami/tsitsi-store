document.addEventListener('DOMContentLoaded', function() {
    const drawer = document.getElementById('myDrawer');
    const overlay = document.getElementById('drawerOverlay');
    const closeBtn = document.getElementById('closeDrawerBtn');
    
    // Bouton de la Navbar (Haut)
    const openBtnNav = document.getElementById('openDrawerBtn');
    // Bouton de la barre mobile (Bas)
    const openBtnMobile = document.getElementById('openDrawerBtnMobile');

    function openDrawer() {
        drawer.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Empêche le scroll derrière
    }

    function closeDrawer() {
        drawer.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = 'auto';
    }

    if (openBtnNav) openBtnNav.addEventListener('click', openDrawer);
    if (openBtnMobile) openBtnMobile.addEventListener('click', openDrawer);
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (overlay) overlay.addEventListener('click', closeDrawer);

    let lastScrollTop = 0;
    const mobileBar = document.querySelector('.mobile-nav-bar');

    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (window.innerWidth < 992) { // Uniquement sur mobile
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // On descend : on cache la barre
                mobileBar.style.transform = "translateY(100%)";
                mobileBar.style.transition = "transform 0.3s ease-in-out";
            } else {
                // On remonte : on montre la barre
                mobileBar.style.transform = "translateY(0)";
            }
        }
        lastScrollTop = scrollTop;
    });
});