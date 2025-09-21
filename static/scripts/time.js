function updateTime() {
    try {
        const dateHeader = document.querySelector("h5#date");
        const timeHeader = document.querySelector("h4#time");
        const now = new Date();

        const dateOptions = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        };

        const timeOptions = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };

        dateHeader.textContent = now.toLocaleDateString(undefined, dateOptions);
        timeHeader.textContent = now.toLocaleTimeString(undefined, timeOptions);
    } catch (e) {
        console.log(e)
    }
}

setInterval(updateTime, 1000);
updateTime();