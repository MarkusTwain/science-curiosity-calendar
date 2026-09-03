# Science & Curiosity Calendar

A lightweight, dependency-free front-end prototype for a weekly science/discovery calendar.

## Run it

Open `index.html` in a browser. No server is required for the prototype.

## Add real stories

Edit `data.js`. Each story has:

- `date`: YYYY-MM-DD
- `category`
- `title`
- `summary`
- `why`
- `source`
- `url`

## Turn it into an automatically updated site

The front-end is deliberately separated from the data. A production version can have a small scheduled backend that:

1. Collects RSS/API results from selected reputable sources.
2. Deduplicates stories.
3. Classifies them into categories.
4. Scores them for novelty/interestingness.
5. Generates a 2–4 sentence summary and a "Why it's interesting" line.
6. Writes the resulting records to a JSON/database endpoint.
7. The webpage fetches that data instead of the demo `data.js`.

For publication, the simplest hosting options are GitHub Pages, Cloudflare Pages, Netlify, or Vercel. A scheduled collector can run separately (for example, once per day).

Important: preserve the original article URL and source, and clearly distinguish publication date from event/occurrence date when they differ.
