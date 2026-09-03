const state = {
  weekStart: startOfWeek(new Date()),
  category: "All",
  query: ""
};

const calendar = document.getElementById("calendar");
const filters = document.getElementById("filters");
const weekTitle = document.getElementById("weekTitle");
const weekSubtitle = document.getElementById("weekSubtitle");
const dialog = document.getElementById("articleDialog");
const dialogContent = document.getElementById("dialogContent");

const preferredOrder = ["All", "Science", "Space", "Nature", "Archaeology", "AI & Robotics", "Technology", "Celebration"];
const categories = preferredOrder.filter(c => c === "All" || STORIES.some(s => s.category === c));

function pad(n) { return String(n).padStart(2, "0"); }
function iso(d) { return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; }
function startOfWeek(d) {
  const x = new Date(d);
  x.setHours(0,0,0,0);
  const day = x.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  x.setDate(x.getDate() + diff);
  return x;
}
function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate()+n); return x; }
function formatDate(d, opts={}) {
  return new Intl.DateTimeFormat("en", opts).format(d);
}
function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
}

function renderFilters() {
  filters.innerHTML = categories.map(c =>
    `<button class="filter ${state.category===c ? "active":""}" data-category="${escapeHtml(c)}">${escapeHtml(c)}</button>`
  ).join("");
  filters.querySelectorAll(".filter").forEach(btn => btn.onclick = () => {
    state.category = btn.dataset.category; render();
  });
}

function matches(story) {
  const q = state.query.toLowerCase().trim();
  const categoryOk = state.category === "All" || story.category === state.category;
  const text = `${story.title} ${story.summary} ${story.why} ${story.category} ${story.source}`.toLowerCase();
  return categoryOk && (!q || text.includes(q));
}

function render() {
  renderFilters();
  const end = addDays(state.weekStart, 6);
  weekTitle.textContent = `${formatDate(state.weekStart,{day:"numeric",month:"short"})} — ${formatDate(end,{day:"numeric",month:"short",year:"numeric"})}`;
  weekSubtitle.textContent = "Real science, space, nature, archaeology, AI & robotics, technology and curiosity news.";
  const today = iso(new Date());
  calendar.innerHTML = "";

  for (let i=0; i<7; i++) {
    const date = addDays(state.weekStart, i);
    const dateStr = iso(date);
    const stories = STORIES.filter(s => s.date === dateStr && matches(s));

    const day = document.createElement("article");
    day.className = `day ${dateStr===today ? "today":""}`;
    day.innerHTML = `
      <div class="day-head">
        <div class="day-name">${formatDate(date,{weekday:"short"}).toUpperCase()}</div>
        <div class="day-date">${formatDate(date,{day:"numeric",month:"short"})}</div>
      </div>
      <div class="stories">
        ${stories.length ? stories.map(cardHtml).join("") : `<div class="empty">No matching stories</div>`}
      </div>`;
    calendar.appendChild(day);
  }

  calendar.querySelectorAll(".card").forEach(card => {
    card.onclick = () => openStory(Number(card.dataset.index));
  });
  renderArchive();
}

function cardHtml(story) {
  const index = STORIES.indexOf(story);
  return `<div class="card" data-index="${index}">
    <div class="card-top"><span class="tag">${escapeHtml(story.category)}</span><span class="read-time">2 min</span></div>
    <h4>${escapeHtml(story.title)}</h4>
    <p>${escapeHtml(story.summary)}</p>
    <div class="card-source">${escapeHtml(story.source)}</div>
  </div>`;
}

function openStory(index) {
  const s = STORIES[index];
  dialogContent.innerHTML = `
    <span class="eyebrow">${escapeHtml(s.category)}</span>
    <h2 class="dialog-title">${escapeHtml(s.title)}</h2>
    <div class="dialog-meta">${formatDate(new Date(s.date+"T12:00:00"),{weekday:"long",day:"numeric",month:"long",year:"numeric"})} · ${escapeHtml(s.source)}</div>
    <p class="dialog-summary">${escapeHtml(s.summary)}</p>
    <div class="why"><strong>Why it's interesting</strong><br>${escapeHtml(s.why)}</div>
    <a class="source-btn" href="${escapeHtml(s.url)}" target="_blank" rel="noopener">Read original source ↗</a>`;
  dialog.showModal();
}

function renderArchive() {
  const weeks = [...new Set(STORIES.map(s => iso(startOfWeek(new Date(s.date+"T12:00:00")))))].sort().reverse();
  const archive = document.getElementById("archiveList");
  archive.innerHTML = weeks.map(w => {
    const d = new Date(w+"T12:00:00"), e = addDays(d,6);
    return `<button class="archive-item" data-week="${w}">${formatDate(d,{day:"numeric",month:"short"})} — ${formatDate(e,{day:"numeric",month:"short",year:"numeric"})}</button>`;
  }).join("") || `<span class="muted">No archived weeks yet.</span>`;
  archive.querySelectorAll(".archive-item").forEach(b => b.onclick = () => {
    state.weekStart = new Date(b.dataset.week+"T12:00:00"); render();
    window.scrollTo({top:0, behavior:"smooth"});
  });
}

document.getElementById("prevWeek").onclick = () => { state.weekStart = addDays(state.weekStart,-7); render(); };
document.getElementById("nextWeek").onclick = () => { state.weekStart = addDays(state.weekStart,7); render(); };
document.getElementById("todayBtn").onclick = () => { state.weekStart = startOfWeek(new Date()); render(); };
document.getElementById("searchInput").oninput = e => { state.query=e.target.value; render(); };
document.getElementById("closeDialog").onclick = () => dialog.close();
dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });

document.getElementById("themeBtn").onclick = () => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = dark ? "" : "dark";
  localStorage.setItem("theme", dark ? "light" : "dark");
};
if (localStorage.getItem("theme")==="dark") document.documentElement.dataset.theme="dark";

render();
