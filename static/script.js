// ✅ FILTER FUNCTION (for buttons: All / Easy / Medium / Hard)
function filterTasks(level) {
    const tasks = document.querySelectorAll(".task-card");

    tasks.forEach(task => {
        if (level === "all") {
            task.style.display = "flex";
        } else {
            if (task.classList.contains(level)) {
                task.style.display = "flex";
            } else {
                task.style.display = "none";
            }
        }
    });
}