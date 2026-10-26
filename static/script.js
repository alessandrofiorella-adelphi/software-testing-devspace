function toggleVisibility() {
    var element = document.getElementById("newBuild");
    element.toggleAttribute("hidden");
}

document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('buildTable');
    const overlay = document.getElementById('cardOverlay');
    const uploadBtn = document.getElementById('uploadBuildTriggerBtn');
    const newBuildCard = document.getElementById('newBuild');
    const editBuildCard = document.getElementById('editBuildCard');
    const editForm = document.getElementById('editBuildForm');

    if (uploadBtn && newBuildCard) {
        uploadBtn.addEventListener('click', (e) => {
            newBuildCard.classList.remove('hidden-card');
            newBuildCard.classList.add('expanded');
            document.body.classList.add('card-open');
            e.stopPropagation();
        });

        newBuildCard.addEventListener('click', (e) => {
            const isCloseButton = e.target.classList.contains('close-card-btn');
            if (isCloseButton) {
                newBuildCard.classList.add('hidden-card');
                closeActiveCard();
            }
        });
    }

    if (editBuildCard) {
        editBuildCard.addEventListener('click', (e) => {
            const isCloseButton = e.target.classList.contains('close-card-btn');
            if (isCloseButton) {
                editBuildCard.classList.add('hidden-card');
                closeActiveCard();
            }
        });
    }

    if (!table) return;

    table.addEventListener('click', (e) => {
        const card = e.target.closest('.display-container');
        if (!card) return;

        const isCloseButton = e.target.classList.contains('close-card-btn');
        const isEditButton = e.target.classList.contains('edit-card-trigger-btn');
        const isFormAction = e.target.closest('form') || e.target.closest('button:not(.button)');

        if (isCloseButton) {
            closeActiveCard();
            return;
        }

        if (isEditButton) {
            if (editBuildCard && editForm) {
                const bId = card.getAttribute('data-id');
                const bName = card.getAttribute('data-name');
                const bDesc = card.getAttribute('data-description');
                const bInst = card.getAttribute('data-instructions');
                const bLink = card.getAttribute('data-link');
                const bTag = card.getAttribute('data-tag');

                closeActiveCard();

                editForm.action = "/editBuild/" + bId;
                document.getElementById('editBuildName').value = bName;
                document.getElementById('editDescription').value = bDesc;
                document.getElementById('editInstructions').value = bInst;
                document.getElementById('editLink').value = bLink;
                document.getElementById('editTag').value = bTag;

                editBuildCard.classList.remove('hidden-card');
                editBuildCard.classList.add('expanded');
                document.body.classList.add('card-open');
            }
            return;
        }

        if (card.classList.contains('expanded')) {
            return;
        }

        if (!isFormAction || e.target.classList.contains('button')) {
            card.classList.add('expanded');
            document.body.classList.add('card-open');
        }
    });

    if (overlay) {
        overlay.addEventListener('click', closeActiveCard);
    }

    function closeActiveCard() {
        const expandedCard = document.querySelector('.display-container.expanded');
        if (expandedCard) {
            expandedCard.classList.remove('expanded');
            if (expandedCard.id === 'newBuild' || expandedCard.id === 'editBuildCard') {
                expandedCard.classList.add('hidden-card');
            }
        }
        document.body.classList.remove('card-open');
    }
});
