const navbar = document.querySelector("nav");
        
window.addEventListener("scroll", function () {
    if (window.scrollY === 0) {
        // User is at the top of the page → Show nav
        navbar.style.top = "0";
    } else {
        // User scrolled down → Hide nav
        navbar.style.top = "-70px"; // Adjust based on nav height
    }
});