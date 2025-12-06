let currentSlug = null;

async function refreshSongs(){
  // Fetch the list of songs from the backend
  const res = await fetch('/api/songs');
  const list = await res.json();

  // Get the <select> element and clear existing options
  const sel = document.getElementById('song-select');
  sel.innerHTML = '';

  // Add a placeholder option so nothing is selected by default on page load.
  const placeholder = document.createElement('option');
  placeholder.value = '';                       // empty value indicates no song
  placeholder.text = '— Select a song —';
  placeholder.selected = true;
  placeholder.disabled = true;                  // keep it as a non-selectable placeholder
  sel.appendChild(placeholder);

  // Populate options for each song (do NOT auto-select or load them)
  list.forEach(s=>{
    const opt = document.createElement('option');
    opt.value = s.slug;
    opt.text = s.name + ' (' + s.slug + ')';
    sel.appendChild(opt);
  });

  // If we already had currentSlug (e.g. after creating a song), restore selection.
  if (currentSlug) {
    const exists = list.some(it => it.slug === currentSlug);
    if (exists) {
      sel.value = currentSlug;
    } else {
      // if the previously selected song no longer exists, reset currentSlug
      currentSlug = null;
    }
  }
}

async function createSong(){
  const name = document.getElementById('new-song-name').value || 'untitled';
  const res = await fetch('/api/songs', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({name})
  });
  const j = await res.json();
  if(j.created){
    // Refresh the song list and select/load the new song for convenience.
    await refreshSongs();
    document.getElementById('new-song-name').value = '';
    currentSlug = j.slug;
    const sel = document.getElementById('song-select');
    sel.value = j.slug;   // select the newly created song
    loadSong();           // load it immediately so user can start uploading/transcribing
  } else {
    alert(JSON.stringify(j));
  }
}

async function loadSong(){
  const sel = document.getElementById('song-select');
  if(!sel.value) return;  // if placeholder or nothing selected, do nothing
  const slug = sel.value;
  currentSlug = slug;
  const res = await fetch('/api/songs/' + encodeURIComponent(slug));
  const meta = await res.json();
  if(meta.error){ alert(meta.error); return; }
  document.getElementById('song-area').style.display = 'block';
  document.getElementById('song-title').textContent = meta.name + ' or slugname:' + meta.slug;
  // files
  const filesDiv = document.getElementById('files');
  filesDiv.innerHTML = '';
  (meta.files || []).forEach(f=>{
    const url = '/api/songs/' + encodeURIComponent(slug) + '/files/' + encodeURIComponent(f);
    const ext = f.split('.').pop().toLowerCase();
    const img = document.createElement('img');
    img.className = 'thumb';
    img.src = (ext==='txt' ? '/static/text-file.png' : url);
    img.alt = f;
    img.title = f;
    img.onclick = ()=> previewFile(url);
    filesDiv.appendChild(img);
  });
  // notes
  document.getElementById('notes-list').textContent = JSON.stringify(meta.notes || [], null, 2);
  document.getElementById('tabs-view').textContent = '';
  document.getElementById('ranking').innerHTML = '';
  document.getElementById('preview-img').style.display='none';
}

function previewFile(url){
  document.getElementById('preview-img').src = url;
  document.getElementById('preview-img').style.display='block';
}

async function uploadFile(){
  if(!currentSlug) return alert('Select a song first');
  const f = document.getElementById('file-input').files[0];
  if(!f) return alert('Choose a file');
  const fd = new FormData();
  fd.append('file', f);
  const res = await fetch('/api/songs/' + encodeURIComponent(currentSlug) + '/upload', {method:'POST', body: fd});
  const j = await res.json();
  if(j.saved){ loadSong(); }
  else alert(JSON.stringify(j));
}

async function addNotes(){
  if(!currentSlug) return alert('Select a song first');
  const raw = document.getElementById('manual-notes').value;
  if(!raw) return alert('Enter notes first');
  const res = await fetch('/api/songs/' + encodeURIComponent(currentSlug) + '/add-notes', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({notes: raw})
  });
  const j = await res.json();
  if(j.added) { document.getElementById('manual-notes').value=''; loadSong(); }
  else alert(JSON.stringify(j));
}

async function transcribe(){
  if(!currentSlug) return alert('Select a song first');
  const res = await fetch('/api/songs/' + encodeURIComponent(currentSlug) + '/transcribe');
  const j = await res.json();
  if(j.error) return alert(JSON.stringify(j));
  // show ranking by percent (results already sorted by percent desc)
  const ranking = document.getElementById('ranking');
  ranking.innerHTML = '';
  (j.results || []).forEach(r=>{
    const el = document.createElement('div');
    el.className = 'key-item';
    el.textContent = r.harmonica + ' — ' + (r.percent ? r.percent.toFixed(1) : '0') + '%';
    el.onclick = ()=> showTabs(r);
    ranking.appendChild(el);
  });
  // optionally show easy results below if checkbox checked
  if(document.getElementById('easy-only').checked && (j.easy_results || []).length){
    const header = document.createElement('div'); header.textContent='(Easy results)'; header.style.fontWeight='bold';
    ranking.appendChild(header);
    (j.easy_results || []).forEach(r=>{
      const el = document.createElement('div');
      el.className = 'key-item';
      el.textContent = r.harmonica + ' — ' + (r.percent ? r.percent.toFixed(1) : '0') + '%';
      el.onclick = ()=> showTabs(r);
      ranking.appendChild(el);
    });
  }
}

function showTabs(r){
  // r expected to have tabs, notes, octave_shift, percent
  document.getElementById('tabs-view').textContent =
    'Harmonica: ' + r.harmonica + '\n' +
    'Percent available: ' + (r.percent ? r.percent.toFixed(1) : '0') + '%\n' +
    'Octave shift: ' + (r.octave_shift || 0) + '\n' +
    'Notes used: ' + JSON.stringify(r.notes || []) + '\n' +
    'Tabs: ' + JSON.stringify(r.tabs || [], null, 2);
}

// Initialize the page by populating the song selector (but do not auto-load)
refreshSongs();