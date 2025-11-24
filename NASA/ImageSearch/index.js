/*
    Insert your NASA API key below if you want to include it in requests.
    The NASA Image and Video Library endpoints generally work without an API key, but
    you can add `&api_key=YOUR_NASA_API_KEY_HERE` to the URL if you have one.
*/
const NASA_API_KEY = 'YOUR_NASA_API_KEY_HERE'; // <- Replace with your key if desired

// DOM elements
const qInput = document.getElementById('q');
const searchBtn = document.getElementById('searchBtn');
const thumbsEl = document.getElementById('thumbs');
const detailEl = document.getElementById('detail');
const statusEl = document.getElementById('status');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageNumberEl = document.getElementById('pageNumber');

// Application state
let currentQuery = '';
let currentPage = 1;
let isLoading = false;
let lastRequestId = 0; // used to ignore stale responses

// Utility: set loading state (disables actions to prevent duplicate requests)
function setLoading(loading){
    isLoading = loading;
    statusEl.style.display = loading ? 'block' : 'none';
    searchBtn.disabled = loading;
    prevBtn.disabled = loading || currentPage <= 1;
    nextBtn.disabled = loading;
}

// Perform a search using the NASA Image and Video Library API
// Pagination is implemented with the `page` parameter (page=1,2,...)
async function performSearch(query, page = 1){
    if (!query) return;
    currentQuery = query;
    currentPage = page;
    lastRequestId += 1;
    const requestId = lastRequestId;

    setLoading(true);
    statusEl.textContent = 'Searching...';
    thumbsEl.innerHTML = '';

    // Build the search URL. We hardcode media_type=image per requirements.
    const base = 'https://images-api.nasa.gov/search';
    const params = new URLSearchParams({q: query, media_type: 'image', page: String(page)});
    // Optionally include API key if provided
    if (NASA_API_KEY && NASA_API_KEY !== 'YOUR_NASA_API_KEY_HERE') params.append('api_key', NASA_API_KEY);

    try{
    const resp = await fetch(base + '?' + params.toString());
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    const data = await resp.json();

    // If another newer request was started meanwhile, ignore this response
    if (requestId !== lastRequestId) return;

    renderThumbnails(data);
    }catch(err){
    thumbsEl.innerHTML = '';
    statusEl.style.display = 'block';
    statusEl.className = 'error';
    statusEl.textContent = 'Error loading results: ' + err.message;
    }finally{
    // restore status style
    statusEl.className = 'loading';
    setLoading(false);
    updatePaginationControls();
    }
}

// Map thumbnails from API response to DOM
// The API response has `collection.items[]`; each item may include a `links[]`
// where images (thumbnails/previews) are provided. We pick a reasonable small image from there.
function renderThumbnails(apiData){
    const items = apiData && apiData.collection && apiData.collection.items ? apiData.collection.items : [];
    thumbsEl.innerHTML = '';

    if (!items.length){
    statusEl.style.display = 'block';
    statusEl.textContent = 'No results found';
    return;
    }

    statusEl.style.display = 'none';

    // For each item, build a thumbnail card
    items.forEach(item => {
    // Find a link that is an image (thumbnail). `links` may be missing; fallback to data href.
    const thumbUrl = getThumbnailFromItem(item);
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
    div.addEventListener('click', () => onThumbnailClicked(item));
    div.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') onThumbnailClicked(item); });

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

// Called when a thumbnail is clicked. Fetch asset list to pick a good-resolution image.
async function onThumbnailClicked(item){
    if (!item || !item.data || !item.data[0]) return;
    const meta = item.data[0];
    const nasa_id = meta.nasa_id;

    // Show interim loading UI in the detail pane
    detailEl.innerHTML = '<div class="loading">Loading image...</div>';

    try{
    const assetUrl = `https://images-api.nasa.gov/asset/${encodeURIComponent(nasa_id)}`;
    // optionally include API key
    const url = NASA_API_KEY && NASA_API_KEY !== 'YOUR_NASA_API_KEY_HERE' ? assetUrl + '?api_key=' + NASA_API_KEY : assetUrl;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Asset error: ${resp.status}`);
    const assetData = await resp.json();

    const best = pickBestImageFromAsset(assetData);
    renderFullImage({title: meta.title, description: meta.description || meta.description_508 || meta.photographer || '', imageUrl: best, meta});
    }catch(err){
    detailEl.innerHTML = '<div class="error">Error loading image: ' + err.message + '</div>';
    }
}

// Choose a reasonable image URL from the asset endpoint response
function pickBestImageFromAsset(assetData){
    // assetData.collection.items is usually an array with many variants; prefer high-resolution jpg
    const items = assetData && assetData.collection && assetData.collection.items ? assetData.collection.items : [];
    // Filter images
    const images = items.map(i => i.href).filter(h => typeof h === 'string' && /\.(jpe?g|png)$/i.test(h));
    if (!images.length) return items[0] && items[0].href;
    // Try to pick the largest (often last entries are higher rez) — pick the last jpg/png
    return images[images.length - 1];
}

// Render the full image and metadata in the right pane
function renderFullImage({title, description, imageUrl, meta}){
    const wrapper = document.createElement('div');
    wrapper.className = 'detail';

    const img = document.createElement('img');
    img.src = imageUrl || '';
    img.alt = title || 'NASA Image';

    const info = document.createElement('div');
    info.className = 'info';
    const h2 = document.createElement('h2');
    h2.textContent = title || '';
    const p = document.createElement('p');
    p.textContent = description || (meta && meta.title) || '';

    info.appendChild(h2);
    info.appendChild(p);

    wrapper.appendChild(img);
    wrapper.appendChild(info);

    detailEl.innerHTML = '';
    detailEl.appendChild(wrapper);
}

// Update pagination controls and page indicator
function updatePaginationControls(){
    pageNumberEl.textContent = currentPage;
    prevBtn.disabled = isLoading || currentPage <= 1;
    // nextBtn remains enabled unless loading; API may return empty pages which we handle on render
}

// Wire up button events
searchBtn.addEventListener('click', () => {
    const q = qInput.value.trim();
    if (!q || isLoading) return;
    currentPage = 1;
    performSearch(q, currentPage);
});

// Enter key triggers search
qInput.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') searchBtn.click(); });

prevBtn.addEventListener('click', () => {
    if (isLoading || currentPage <= 1) return;
    currentPage = Math.max(1, currentPage - 1);
    performSearch(currentQuery, currentPage);
});
nextBtn.addEventListener('click', () => {
    if (isLoading) return;
    currentPage = currentPage + 1;
    performSearch(currentQuery, currentPage);
});

// Initial state
setLoading(false);

/*
    Notes:
    - Pagination: the NASA API supports `page` parameter. We pass the page number when calling the
    search endpoint: `...?q={query}&media_type=image&page={page}`.
    - Thumbnails mapping: `renderThumbnails` iterates `collection.items` and picks the first
    image link from `item.links` (commonly a low-resolution preview) and displays it in the grid.
    - Full image: when a thumbnail is clicked we call `/asset/{nasa_id}` to receive a list of
    available files, then choose a high-resolution JPG/PNG.
*/
