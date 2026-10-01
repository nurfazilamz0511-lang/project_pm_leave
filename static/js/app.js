const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");

if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

document.addEventListener("click", (event) => {
    if (window.innerWidth <= 900 && sidebar && sidebar.classList.contains("open")) {
        if (!sidebar.contains(event.target) && event.target !== menuBtn) {
            sidebar.classList.remove("open");
        }
    }
});
