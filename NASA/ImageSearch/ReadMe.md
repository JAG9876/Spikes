## NASA image search - single web page created with perplexity.ai prompts
### Default underlying prompt used:
Space title: 'Frontend using Python'
Space prompt: This space creates prompts for creating web frontends. It guides GitHub Copilot in VS Code to build frontend solutions.
### What was done:
#### 1) Add specific prompt:
Create a prompt that enables me to get a webpage solution where I can search for images throug NASA's 'NASA Image and Video Library API'-API which is described in its own section in this link: https://api.nasa.gov/. Show the results as thumbnail images on the left side of the webpage, but make the results paginated (with buttons to go left and right). When clicking a thumbnail image, the full image is shown on the right side of the webpage.
#### 2) Create the perplexity prompt
See what Perplexity created at the end of this ReadMe.
#### 3) Copy the perplexity prompt and run it in VS Code in the GitHub Copilot chat window.
#### Note:
The prompt created a long index.html file, so I separated it into html-, script- and styling files. One could have made that as part of the default prompt since that is a pretty normal thing to do.

#### Perplexity created this prompt:
Use this prompt with your coding assistant or generator to get the webpage you described:

***
Create a responsive single-page web app (HTML, CSS, and vanilla JavaScript) that searches images using NASA’s “NASA Image and Video Library API” (the images.nasa.gov API documented in the “NASA Image and Video Library API” section at https://api.nasa.gov/).[1][2]

Requirements:

1. General
- Use only client-side code: a single HTML file with embedded or linked CSS and JavaScript.
- Do not use any frameworks (no React, Vue, Angular, jQuery, Bootstrap, etc.).
- Assume the user will provide their own NASA API key where needed; include a clear placeholder like `YOUR_NASA_API_KEY_HERE` and brief comment.

2. Layout
- Split the page into two main columns:
  - Left column: search controls at the top and a scrollable area below that shows image search results as thumbnails in a grid or vertical list.
  - Right column: an area that displays the currently selected full-size image (or a large version of it) with its title and description when a thumbnail is clicked.
- Make the layout responsive so that on smaller screens the right column stacks below the left column.

3. Search functionality
- At the top of the left column, add:
  - A text input for the search query.
  - An optional media type filter that is fixed to images only (you can hardcode `media_type=image` in the API request).
  - A “Search” button that triggers a request to the NASA Image and Video Library search endpoint (for example `https://images-api.nasa.gov/search` with query parameter `q` and `media_type=image`).[3][1]
- When the user submits a search, call the API and display the results as image thumbnails in the results area.

4. Pagination
- Use the NASA Image and Video Library API’s built-in pagination support (e.g., use the `page` query parameter when calling the search endpoint).[4][1]
- Show pagination controls below (or above and below) the thumbnail area:
  - A “Previous” button that loads the previous page of results (disabled on the first page).
  - A “Next” button that loads the next page of results.
  - A simple indicator of the current page number.
- When switching pages, update only the thumbnails and keep the current search query and filters.

5. Thumbnails (left side)
- For each item returned by the API that is an image, display:
  - A thumbnail image (use one of the URLs from the item’s `links` or `href` that points to a small image size if available).[1][3]
  - Optionally the image title or a short caption below the thumbnail.
- Clicking on a thumbnail:
  - Should not reload the page.
  - Should update the right column to show that image in a larger size along with its title and description (if available in the `data` object).

6. Full image view (right side)
- When a thumbnail is clicked:
  - Fetch and display the best available image URL from the item (e.g., via the “asset” endpoint if needed, such as `https://images-api.nasa.gov/asset/{nasa_id}`, and choose a reasonable resolution image).[3][1]
  - Show:
    - The large image.
    - The image title.
    - The description or summary text if available.
- Before anything is selected, show a placeholder message like “Select an image from the left” in the right pane.

7. UX and error handling
- Show a loading indicator or message while a search request is in progress.
- Handle errors gracefully:
  - If the API call fails, show an error message in the results area.
  - If no results are found, display a “No results found” message instead of empty space.
- Prevent duplicate requests while a search is already in progress (e.g., disable the Search button or ignore additional clicks).
- Make sure rapid navigation through pages still works correctly and updates the thumbnails to the latest response only.

8. Code quality
- Use modern JavaScript (ES6+), `fetch`, and `async/await`.
- Organize the JavaScript into small, well-named functions (e.g., `performSearch`, `renderThumbnails`, `renderFullImage`, `updatePaginationControls`).
- Add concise comments explaining:
  - Where to insert the NASA API key if applicable.
  - How pagination is implemented with the `page` parameter.
  - How thumbnails are mapped from the API response to the DOM.

Output:
- Provide the complete `index.html` file, including CSS (either in a `<style>` block or external file reference) and JavaScript (either in a `<script>` block or clearly separated `<script src>` with the code shown).
- Ensure the example is ready to run locally in a browser after inserting a NASA API key if required.

[1](https://api.nasa.gov/assets/json/apis.json)
[2](https://www.re3data.org/repository/r3d100012503)
[3](https://gist.github.com/cgobat/73b9deaba6ae0f60f0abaf4bc2304773)
[4](https://github.com/Sonnerz/project02-interactive-frontend)
[5](https://svs.gsfc.nasa.gov/help/)
[6](https://www.youtube.com/watch?v=Sza6mmt-D0U)
[7](https://cmr.earthdata.nasa.gov/search/site/docs/search/api)
[8](https://www.youtube.com/watch?v=JfXp_YEQRRI)
[9](https://cran.r-project.org/web/packages/nasa/nasa.pdf)
[10](https://wilsjame.github.io/how-to-nasa/)
***
