function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}
// Close sidebar on outside click (mobile)
document.addEventListener('click', e => {
  const sb = document.getElementById('sidebar');
  if (window.innerWidth < 768 && !sb.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
    sb.classList.remove('open');
  }
});

// Para el config del logout en base.html
function toggleSettingsMenu() {
  const menu = document.getElementById("settingsMenu");
  menu.classList.toggle("show");
}


window.addEventListener("click", function(e) {
  const dropdown = document.querySelector(".settings-dropdown");
  if (!dropdown.contains(e.target)) {
    document.getElementById("settingsMenu").classList.remove("show");
  }
});