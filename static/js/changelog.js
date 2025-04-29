document.addEventListener("DOMContentLoaded", function() {
    const tabs = document.querySelectorAll(".tab");
    const sections = document.querySelectorAll(".update-section");

    tabs.forEach(tab => {
        tab.addEventListener("click", function() {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const target = tab.getAttribute("data-target");
            sections.forEach(section => {
                section.classList.add("hidden");
                if (section.id === target) {
                    section.classList.remove("hidden");
                }
            });
        });
    });
});