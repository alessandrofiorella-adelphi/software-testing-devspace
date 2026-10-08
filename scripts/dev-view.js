// WIP: Still not hooked up to anything yet!

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
            const card = e.target.closest('.display-container');
            if (!card) return;

            const isCloseButton = e.target.classList.contains('close-card-btn');
            const isFormAction = e.target.closest('form') || e.target.closest('button');

            // Close the window if the close button is clicked.
            if (isCloseButton) {
                closeActiveCard();
                return;
            }

            // Check if the window is already open.
            if (card.classList.contains('expanded')) {
                return;
            }

            // Open the window.
            if (!isFormAction) {
                card.classList.add('expanded');
                document.body.classList.add('card-open');
            }
        });

        overlay.addEventListener('click', closeActiveCard);

        // Un-expand the card.
        function closeActiveCard() {
            const expandedCard = document.querySelector('.display-container.expanded');
            if (expandedCard) {
                expandedCard.classList.remove('expanded');
            }
            document.body.classList.remove('card-open');
        }
    });