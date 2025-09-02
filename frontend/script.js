document.addEventListener('DOMContentLoaded', () => {
    const notesInput = document.getElementById('notes-input');
    const generateButton = document.getElementById('generate-button');
    const flashcardSection = document.getElementById('flashcard-section');
    const savedFlashcardsDiv = document.getElementById('saved-flashcards');
    const saveFlashcardsButton = document.getElementById('save-flashcards-button');

    let generatedFlashcards = []; // To store flashcards generated from notes

    generateButton.addEventListener('click', async () => {
        const notes = notesInput.value;
        if (!notes) {
            alert('Please paste some notes to generate flashcards.');
            return;
        }

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ notes }),
            });
            const data = await response.json();
            generatedFlashcards = data.flashcards; // Store generated flashcards
            displayFlashcards(generatedFlashcards);
            saveFlashcardsButton.style.display = 'block'; // Show save button
        } catch (error) {
            console.error('Error generating flashcards:', error);
            alert('Failed to generate flashcards. Please try again.');
        }
    });

    saveFlashcardsButton.addEventListener('click', async () => {
        if (generatedFlashcards.length === 0) {
            alert('No flashcards to save.');
            return;
        }

        // For now, using a dummy userId. In a real app, this would come from user authentication.
        const userId = 'testuser123'; 

        try {
            const response = await fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ flashcards: generatedFlashcards, userId }),
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                saveFlashcardsButton.style.display = 'none'; // Hide save button after saving
                generatedFlashcards = []; // Clear generated flashcards after saving
                fetchSavedFlashcards(userId); // Refresh saved flashcards
            } else {
                alert(data.error);
            }
        } catch (error) {
            console.error('Error saving flashcards:', error);
            alert('Failed to save flashcards. Please try again.');
        }
    });

    function displayFlashcards(flashcards) {
        flashcardSection.innerHTML = '';
        flashcards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.classList.add('flashcard');
            cardElement.innerHTML = `
                <div class="flashcard-inner">
                    <div class="flashcard-front">
                        <p>${card.question}</p>
                    </div>
                    <div class="flashcard-back">
                        <p>${card.answer}</p>
                    </div>
                </div>
            `;
            cardElement.addEventListener('click', () => {
                cardElement.classList.toggle('flipped');
            });
            flashcardSection.appendChild(cardElement);
        });
    }

    // Function to fetch and display saved flashcards
    async function fetchSavedFlashcards(userId = 'testuser123') { // Pass userId to fetch
        try {
            const response = await fetch(`/flashcards?userId=${userId}`);
            const data = await response.json();
            displaySavedFlashcards(data.flashcards);
        } catch (error) {
            console.error('Error fetching saved flashcards:', error);
        }
    }

    function displaySavedFlashcards(flashcards) {
        savedFlashcardsDiv.innerHTML = '';
        flashcards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.classList.add('flashcard');
            cardElement.innerHTML = `
                <div class="flashcard-inner">
                    <div class="flashcard-front">
                        <p>${card.question}</p>
                    </div>
                    <div class="flashcard-back">
                        <p>${card.answer}</p>
                    </div>
                </div>
            `;
            cardElement.addEventListener('click', () => {
                cardElement.classList.toggle('flipped');
            });
            savedFlashcardsDiv.appendChild(cardElement);
        });
    }

    // Initial fetch of saved flashcards
    fetchSavedFlashcards();
});
