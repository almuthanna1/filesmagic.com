const toggleButton = document.getElementById("theme-selector");
//const body = document.body;
const root = document.documentElement;

// Function to enable dark mode
function enableDarkMode() {
    root.classList.add("dark");
    localStorage.setItem("darkMode", "enabled");
    toggleButton.textContent = "☀️";
    toggleButton.style.backgroundColor = "white";
}

// Function to disable dark mode
function disableDarkMode() {
    root.classList.remove("dark");
    localStorage.setItem("darkMode", "disabled");
    toggleButton.textContent = "🌙";
    toggleButton.style.backgroundColor = "#333";
}

// Load saved theme preference
if (localStorage.getItem("darkMode") === "enabled") {
    enableDarkMode();
} else {
    disableDarkMode();
}

// Toggle dark mode on button click
toggleButton.addEventListener("click", () => {
    if(root.classList.contains("dark")) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
});
