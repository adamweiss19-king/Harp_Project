 // NOTE: this inline script is identical to what you'll later place in /static/app.js.
        let currentSlug = null;
        async function refreshSongs(){
          const res = await fetch('/api/songs');
          const list = await res.json();
          const sel = document.getElementById('song-select');
          sel.innerHTML = '';
          list.forEach(s=>{
            const opt = document.createElement('option');
            opt.value = s.slug;
            opt.text = s.name + ' (' + s.slug + ')';
            sel.appendChild(opt);
          });
          if(list.length) { sel.selectedIndex = 0; loadSong(); }
        }
        async function createSong(){
          const name = document.getElementById('new-song-name').value || 'untitled';
          const res = await fetch('/api/songs', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({name})
          });
          const j = await res.json();
          if(j.created){ await refreshSongs(); document.getElementById('new-song-name').value=''; }
          else alert(JSON.stringify(j));
        }
        async function loadSong(){
          const sel = document.getElementById('song-select');
          if(!sel.value) return;
          const slug = sel.value;
          currentSlug = slug;
          const res = await fetch('/api/songs/' + encodeURIComponent(slug));
          const meta = await res.json();
          if(meta.error){ alert(meta.error); return; }
          document.getElementById('song-area').style.display = 'block';
          document.getElementById('song-title').textContent = meta.name + ' — ' + meta.slug;
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
            'Harmonica: ' + r.harmonica + '\\n' +
            'Percent available: ' + (r.percent ? r.percent.toFixed(1) : '0') + '%\\n' +
            'Octave shift: ' + (r.octave_shift || 0) + '\\n' +
            'Notes used: ' + JSON.stringify(r.notes || []) + '\\n' +
            'Tabs: ' + JSON.stringify(r.tabs || [], null, 2);
        }

        // init
        refreshSongs();