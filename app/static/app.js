const statusElement = document.getElementById('status');
const notesGridElement = document.getElementById('notes-grid');

function renderNotes(notes) {
  notesGridElement.innerHTML = '';

  if (!notes.length) {
    statusElement.textContent = 'No notes found.';
    return;
  }

  statusElement.textContent = '';

  notes.forEach((note) => {
    const card = document.createElement('article');
    card.className = 'note-card';

    const title = document.createElement('h2');
    title.textContent = note.title || 'Untitled';

    const text = document.createElement('p');
    text.textContent = note.text || '—';

    card.appendChild(title);
    card.appendChild(text);
    notesGridElement.appendChild(card);
  });
}

async function loadNotes() {
  statusElement.textContent = 'Loading notes…';

  try {
    const response = await fetch('/api/notes');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const notes = await response.json();
    renderNotes(notes);
  } catch (_error) {
    notesGridElement.innerHTML = '';
    statusElement.textContent = 'Failed to load notes.';
  }
}

window.addEventListener('DOMContentLoaded', loadNotes);
