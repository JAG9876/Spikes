// DOM elements
const thumbsEl = document.getElementById('thumbs');
const searchBtn = document.getElementById('search-button');
const statusEl = document.getElementById('status');

let isLoading = false;

function searchImages() {
    let searchText = document.getElementById('search-input').value;
    if (!searchText || searchText.toString() === '') {
        alert('Please enter a search term.');
        return;
    }
    performSearch(searchText);
}

async function performSearch(query) {
    console.log('Searching for images with query:', query);

    thumbsEl.innerHTML = ''; // Clear previous results

    setLoading(true);

    // Build url for image search
    const base = 'http://localhost:5000/api/search';
    const params = new URLSearchParams({q: query});

    try{
        const resp = await fetch(base + '?' + params.toString());
        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        const data = await resp.json();

        if (data.errorMessage){
            setErrorMessage(data.errorMessage);
            return;
        }

        renderThumbnails(data.searchResponse);
    }catch(err){
        setErrorMessage(err.message);
    }finally{
        // restore status style
        statusEl.className = 'loading';
        setLoading(false);
    }
}

function setErrorMessage(message) {
    thumbsEl.innerHTML = '';
    statusEl.style.display = 'block';
    statusEl.className = 'error';
    statusEl.textContent = 'Error loading results: ' + message;
}

function setLoading(loading){
    isLoading = loading;
    searchBtn.disabled = loading;
}

function renderThumbnails(apiData) {
    const items = apiData && apiData.collection && apiData.collection.items ? apiData.collection.items : [];
    thumbsEl.innerHTML = '';

    if (!items.length){
        return;
    }

    items.forEach(item => {
        // Find a link that is an image (thumbnail). `links` may be missing; fallback to data href.
        const thumbUrl = getThumbnailFromItem(item);
        //const thumbUrl = '';
        const title = (item.data && item.data[0] && item.data[0].title) || 'Untitled';
        const nasa_id = item.data && item.data[0] && item.data[0].nasa_id;

        const div = document.createElement('div');
        div.className = 'thumb';
        div.tabIndex = 0;

        const img = document.createElement('img');
        img.src = thumbUrl || '';
        img.alt = title;

        const t = document.createElement('div');
        t.className = 't';
        t.textContent = title;

        div.appendChild(img);
        div.appendChild(t);

        // Clicking a thumbnail updates the right pane without reloading
        //div.addEventListener('click', () => onThumbnailClicked(item));
        //div.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') onThumbnailClicked(item); });

        thumbsEl.appendChild(div);
    });
}

// Helper: find a thumbnail URL from an item
function getThumbnailFromItem(item){
    if (!item) return null;
    // `links` commonly contains images with rel=preview; pick first image link
    if (Array.isArray(item.links)){
    const link = item.links.find(l => l.render === 'image' || (l.rel && l.rel.includes('preview')) ) || item.links[0];
    if (link && link.href) return link.href;
    }
    // fallback: sometimes a thumbnail is available in data[0].href (rare)
    return null;
}
