const statusElement = document.getElementById('status');
const notesGridElement = document.getElementById('notes-grid');

function renderNotes(notes) {
  notesGridElement.innerHTML = '';

  if (!notes.length) {
    statusElement.textContent = 'Keine Notizen gefunden.';
    return;
  }

  statusElement.textContent = '';

  notes.forEach((note) => {
    const card = document.createElement('article');
    card.className = 'note-card';

    const title = document.createElement('h2');
    title.textContent = note.title || 'Ohne Titel';

    const text = document.createElement('p');
    text.textContent = note.text || '—';

    card.appendChild(title);
    card.appendChild(text);
    notesGridElement.appendChild(card);
  });
}

async function loadNotes() {
  statusElement.textContent = 'Lade Notizen …';

  try {
    const response = await fetch('/api/notes');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const notes = await response.json();
    renderNotes(notes);
  } catch (_error) {
    notesGridElement.innerHTML = '';
    statusElement.textContent = 'Fehler beim Laden der Notizen.';
  }
}

window.addEventListener('DOMContentLoaded', loadNotes);
