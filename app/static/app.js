const setupPanelElement = document.getElementById('setup-panel');
const setupFormElement = document.getElementById('setup-form');
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

async function showSetupIfNeeded() {
  const response = await fetch('/api/config');

  if (!response.ok) {
    throw new Error('Failed to load configuration status.');
  }

  const payload = await response.json();
  const configured = Boolean(payload.credentials_configured);

  if (configured) {
    setupPanelElement.hidden = true;
    await loadNotes();
    return;
  }

  notesGridElement.innerHTML = '';
  setupPanelElement.hidden = false;
  statusElement.textContent = 'Please configure your Google Keep credentials first.';
}

setupFormElement.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(setupFormElement);
  const email = String(formData.get('email') || '').trim();
  const masterToken = String(formData.get('master_token') || '').trim();

  statusElement.textContent = 'Saving credentials…';

  try {
    const response = await fetch('/api/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        master_token: masterToken,
      }),
    });

    if (!response.ok) {
      throw new Error('Unable to save credentials.');
    }

    setupPanelElement.hidden = true;
    await loadNotes();
  } catch (_error) {
    statusElement.textContent = 'Failed to save credentials. Please check your input.';
  }
});

window.addEventListener('DOMContentLoaded', async () => {
  try {
    await showSetupIfNeeded();
  } catch (_error) {
    statusElement.textContent = 'Failed to initialize app.';
  }
});
