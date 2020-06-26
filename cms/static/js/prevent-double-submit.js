document.addEventListener('DOMContentLoaded', (event) => {
    for (let form of document.forms) {
        let button = form.querySelector('[type=submit]');
        form.addEventListener('submit', () => {
            button.disabled = true;
            setTimeout(() => {
                button.disabled = false;
            }, 5000); // enable button 5 seconds later
        });
    }
});