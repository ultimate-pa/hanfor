document.querySelectorAll('[data-bs-toggle="tab"]').forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(b => {
            b.classList.remove("active");
            b.setAttribute("aria-selected", "false");
        });
        document.querySelectorAll(".tab-pane").forEach(p => {
            p.classList.remove("show", "active");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
        document.querySelector(btn.dataset.bsTarget).classList.add("show", "active");
    });
});