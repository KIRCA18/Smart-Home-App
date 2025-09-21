let input = document.querySelector("#deviceInput");
let select = document.querySelector("#roomSelect");

function search(deviceValue, roomValue) {
    const path = window.location.pathname; // e.g. "/devices/"

    const params = new URLSearchParams();

    if (deviceValue) params.set("device", deviceValue);
    if (parseInt(roomValue)) params.set("room", roomValue);

    const url = `${path}?${params.toString()}`;

    console.log("Requesting:", url);
    window.location.href = url;
}

let funcID;

input.addEventListener("input", (e) => {
    if (funcID) {
        clearTimeout(funcID);
    }

    const deviceValue = e.target.value;
    const roomValue = select.value;

    funcID = setTimeout(() => {
        search(deviceValue, roomValue);
    }, 500);
});

select.addEventListener("change", (e) => {
    const deviceValue = input.value;
    const roomValue = e.target.value;

    // No debounce here — run immediately on room change
    search(deviceValue, roomValue);
});