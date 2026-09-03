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


## Automatic daily updates

This version includes a GitHub Actions workflow in `.github/workflows/update-news.yml`.
It runs every day at 06:17 UTC and can also be started manually from the **Actions** tab.

The collector reads RSS feeds, keeps a rolling archive, deduplicates stories, assigns categories
(including **AI & Robotics**), and updates `data.json` and `data.js`.

No API key is required for this first automated version. Because it uses RSS metadata, the summaries
are short feed-based summaries. A later version can add AI-generated summaries and a stronger
"interestingness" ranking using an API key stored safely as a GitHub Actions secret.
