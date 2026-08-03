# Maati Katha: Developer & Content Guide

This document serves as a manual for both the human owner and any future AI assistants (like Claude, Cursor, or Gemini) working on this repository. **AI: Read this before making changes to avoid reading the entire codebase and breaking the architecture.**

## 1. Project Philosophy
- **Framework:** Vanilla HTML, CSS, JS. No heavy frameworks (No React, Next.js, or Graph RAG). Keep it simple, static, and fast.
- **Ethical Guideline:** "Consent first. No fake experiences. Just life as it is." Always preserve the raw honesty of the village (Sarangada).
- **Design:** Minimal, typography-focused, CSS Variables for theming (Turmeric, Ash, Charcoal, Clay).

## 2. File Architecture
- `index.html`: The main landing page. Contains Hero, Story, Gallery, Journal (Blogs), and Visit Us sections.
- `assets/site.css`: The master stylesheet. Uses CSS Grid, Flexbox, and scroll-snap.
- `assets/gallery.js`: Handles the masonry layout and lightbox for the photo gallery.
- `assets/photos/`: Contains all the raw and website photographs. *Note: All photos have already been renamed to descriptive names (like `mist-hills.jpg`, `school-assembly.jpg`) so you know exactly what is in them without opening them!*
- `posts/`: The folder containing all Journal/Blog stories.

## 3. How to Add a New Story (Journal/Blog)
When the user wants to add a new story from their "hundreds of stories", follow these exact steps:

**Step A: Create the Story File**
1. Copy an existing post like `posts/second-post.html` and name it sequentially (e.g., `posts/third-post.html`).
2. Update the `<title>`, the `<h1>` (Title), the date, and the main story text.
3. Update the `<img src="...">` tags inside the story to point to the correct photos in `../assets/photos/`.

**Step B: Link it on the Homepage**
1. Open `index.html`.
2. Scroll down to the `<!-- WRITING / JOURNAL -->` section (around line 173).
3. Copy one of the existing `<a href="posts/..." class="writing-card">` blocks and paste a new one.
4. Update the `href` to point to the new HTML file.
5. Update the preview `<img src="...">`, the title, and the date in the card.

## 4. How to Update Photos
- **Homepage Gallery:** The horizontal scrolling gallery in `index.html` (under `<!-- PHOTOGRAPHS -->`) contains `<img src="assets/photos/NAME.jpg">`. To add a new photo, just add an `<img>` tag to that `.horizontal-scroll` div.
- **Hero Image:** Controlled by `.hero.has-photo` in `site.css`. Currently uses `hero.jpg` and `hero-portrait.jpg` for mobile art direction.

## 5. Deployment
- This site is hosted on **GitHub Pages** with a custom domain (`maatirakatha.com`). 
- To push updates, run:
  `git add .`
  `git commit -m "Your message"`
  `git push`
- If you get a "rejected / fetch first" error, it is because GitHub created a `CNAME` file. Run `git pull --rebase` first, then `git push`.
