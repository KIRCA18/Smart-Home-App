let expanded = false
let options = document.querySelector("div#house-options")
let chevron = document.querySelector("#house-chevron")
document.querySelector("div#selected-house").addEventListener("click", (e) => {
    console.log(chevron)
    options.style.display = expanded ? "none" : "block"
    chevron.style.transform = expanded ? "none" : "rotate(180deg)"
    expanded = !expanded
})