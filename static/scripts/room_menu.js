let room_menu = document.querySelectorAll(".room_menu")

room_menu.forEach(val => {
    val.addEventListener("click", (e) => {
        let options = val.parentNode.querySelector(".room_options")
        let expanded = options.style.display == "flex"
        options.style.display = expanded ? "none" : "flex"
    })
})