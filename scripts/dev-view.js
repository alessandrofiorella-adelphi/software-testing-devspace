function toggleVisibility() {
    var element = document.getElementById("newBuild");
    // Toggles the 'hidden' class on click
    element.toggleAttribute("hidden");
}
document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('buildTable');
    const overlay = document.getElementById('cardOverlay');

    if (!table) return;

    table.addEventListener('click', (e) => {
        const card = e.target.closest('.build-container');
        if (!card) return;

        const isCloseBtn = e.target.classList.contains('close-card-btn');
        const isFormAction = e.target.closest('form') || e.target.closest('button');

        // Case 1: Clicking the close button
        if (isCloseBtn) {
            closeActiveCard();
            return;
        }

        // Case 2: Card is already open, ignore clicks unless it targets forms
        if (card.classList.contains('expanded')) {
            return;
        }

        // Case 3: Open the card (ignoring accidental triggers on overview action buttons)
        if (!isFormAction) {
            card.classList.add('expanded');
            document.body.classList.add('card-open');
        }
    });

    overlay.addEventListener('click', closeActiveCard);

    function closeActiveCard() {
        const expandedCard = document.querySelector('.build-container.expanded');
        if (expandedCard) {
            expandedCard.classList.remove('expanded');
        }
        document.body.classList.remove('card-open');
    }
});