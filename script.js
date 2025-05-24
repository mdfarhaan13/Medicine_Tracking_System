// static/js/script.js

document.addEventListener('DOMContentLoaded', function () {

    // Fade in body when page loads
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.transition = "opacity 1s";
        document.body.style.opacity = 1;
    }, 100);

    // Highlight navigation buttons on hover
    const navButtons = document.querySelectorAll('.btn');
    navButtons.forEach(btn => {
        btn.addEventListener('mouseover', () => {
            btn.style.transform = 'scale(1.05)';
        });
        btn.addEventListener('mouseout', () => {
            btn.style.transform = 'scale(1)';
        });
    });

    // Sorting table based on expiry date (ascending)
    const sortBtn = document.getElementById('sortByExpiry');
    if (sortBtn) {
        sortBtn.addEventListener('click', () => {
            const table = document.getElementById('medicineTable');
            const rows = Array.from(table.querySelectorAll('tbody tr'));

            rows.sort((a, b) => {
                const dateA = new Date(a.querySelector('.expiry-date').innerText);
                const dateB = new Date(b.querySelector('.expiry-date').innerText);
                return dateA - dateB;
            });

            const tbody = table.querySelector('tbody');
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessage = document.querySelector('.flash-message');
    if (flashMessage) {
        setTimeout(() => {
            flashMessage.style.display = 'none';
        }, 5000);
    }

});
