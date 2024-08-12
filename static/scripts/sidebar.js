let sidebar = document.getElementById('sidebar');
let mainContent = document.querySelector('.main-content');

const state = JSON.parse(localStorage.getItem('sidebar') || 'false')
if ((sidebar.classList.contains('show') && state == false) || (!sidebar.classList.contains('show') && state == true)) {
    toggleSidebar()
}

document.getElementById('sidebarToggle').addEventListener('click', function () {
    toggleSidebar()
});

function toggleSidebar(){
    sidebar.classList.toggle('show');
    mainContent.classList.toggle('sidebar-expanded');
    localStorage.setItem("sidebar", sidebar.classList.contains('show') ? 'true' : 'false')
    document.querySelector('#sidebarToggle > svg').style.transform = mainContent.classList.contains("sidebar-expanded") ? "rotate(0deg)" : "rotate(180deg)"
}