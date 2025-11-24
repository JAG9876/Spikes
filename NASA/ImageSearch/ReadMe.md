## NASA image search - single web page created with perplexity.ai prompts
### Default underlying prompt used:
Space title: 'Frontend using Python'
Space prompt: This space creates prompts for creating web frontends. It guides GitHub Copilot in VS Code to build frontend solutions.
### What was done:
#### 1) Add specific prompt:
Create a prompt that enables me to get a webpage solution where I can search for images throug NASA's 'NASA Image and Video Library API'-API which is described in its own section in this link: https://api.nasa.gov/. Show the results as thumbnail images on the left side of the webpage, but make the results paginated (with buttons to go left and right). When clicking a thumbnail image, the full image is shown on the right side of the webpage.
#### 2) Create the perplexity prompt
#### 3) Copy the perplexity prompt and run it in VS Code in the GitHub Copilot chat window.
#### Note:
The prompt created a long index.html file, so I separated it into html-, script- and styling files. One could have made that as part of the default prompt since that is a pretty normal thing to do.