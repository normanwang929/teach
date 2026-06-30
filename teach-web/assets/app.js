// Teach Platform - app.js
// Course catalog frontend logic

const BASE = '.';
const DATA_URL = `${BASE}/data/courses.json`;

let courses = [];
let currentCategory = 'all';
let currentSort = 'latest';
let searchTerm = '';

// ── Init ────────────────────────────────────────────────────────────────────────
async function init() {
  await loadData();
  renderStats();
  renderCategoryTabs();
  renderCourses();
  renderProgress();
  bindEvents();

  // 监听进度变化（跨标签页同步）
  window.addEventListener('teach-progress-sync', () => {
    renderProgress();
    renderCourses(); // 进度变化后刷新卡片
  });
}

// ── Data ───────────────────────────────────────────────────────────────────────
async function loadData() {
  try {
    const res = await fetch(DATA_URL);
    courses = await res.json();
  } catch (e) {
    courses = getDemoCourses();
  }

  // 合并 localStorage 中的动态进度
  mergeLocalProgress();
}

function mergeLocalProgress() {
  try {
    const saved = localStorage.getItem('teach-progress');
    if (!saved) return;
    const progressData = JSON.parse(saved);
    courses.forEach(c => {
      if (progressData[c.id]) {
        c.progress = progressData[c.id].percent || 0;
        if (c.progress >= 100) c.status = 'completed';
        else if (c.progress > 0) c.status = 'in-progress';
      }
    });
  } catch (e) {}
}

function getDemoCourses() {
  return [
    {
      id: 'typescript-types',
      title: 'TypeScript 类型系统深入',
      desc: '从基础类型到高级类型体操，系统掌握 TypeScript 类型编程',
      category: '编程',
      tags: ['TypeScript', '类型系统', '前端'],
      lessons: 8,
      time: '4小时',
      status: 'not-started',
      progress: 0,
      url: './lessons/0001-typescript-types.html'
    },
    {
      id: 'python-async',
      title: 'Python 异步编程',
      desc: 'async/await、asyncio、并发模型全解析',
      category: '编程',
      tags: ['Python', '异步', '后端'],
      lessons: 6,
      time: '3小时',
      status: 'in-progress',
      progress: 33,
      url: './lessons/0002-python-async.html'
    },
    {
      id: 'llm-basics',
      title: '大语言模型原理',
      desc: 'Transformer 架构、训练方法、提示工程入门',
      category: 'AI',
      tags: ['LLM', 'Transformer', 'AI'],
      lessons: 10,
      time: '6小时',
      status: 'completed',
      progress: 100,
      url: './lessons/0003-llm-basics.html'
    },
    {
      id: 'git-workflow',
      title: 'Git 工作流实战',
      desc: '分支策略、PR 流程、冲突解决',
      category: '工具',
      tags: ['Git', '协作'],
      lessons: 5,
      time: '2小时',
      status: 'not-started',
      progress: 0,
      url: './lessons/0004-git-workflow.html'
    }
  ];
}

function getDemoProgress() {
  return {
    'typescript-types': { completed: [], current: null },
    'python-async': { completed: [1, 2], current: 3 },
    'llm-basics': { completed: [1,2,3,4,5,6,7,8,9,10], current: null },
    'git-workflow': { completed: [], current: null }
  };
}

// ── Render Stats ────────────────────────────────────────────────────────────────
function renderStats() {
  const total = courses.length;
  const completed = courses.filter(c => c.status === 'completed').length;
  const inProgress = courses.filter(c => c.status === 'in-progress').length;
  const totalLessons = courses.reduce((s, c) => s + c.lessons, 0);

  document.getElementById('stats').innerHTML = `
    <div class="stat-item"><span class="stat-value">${total}</span><span class="stat-label">课程</span></div>
    <div class="stat-item"><span class="stat-value">${totalLessons}</span><span class="stat-label">课时</span></div>
    <div class="stat-item"><span class="stat-value">${completed}</span><span class="stat-label">已完成</span></div>
    <div class="stat-item"><span class="stat-value">${inProgress}</span><span class="stat-label">进行中</span></div>
  `;
  document.getElementById('courseCount').textContent = `${total} 门`;
}

// ── Category Tabs ──────────────────────────────────────────────────────────────
function getCategories() {
  const cats = [...new Set(courses.map(c => c.category))];
  return ['全部', ...cats];
}

function renderCategoryTabs() {
  const cats = getCategories();
  const wrap = document.getElementById('categoryTabs');
  wrap.innerHTML = cats.map(c => {
    const cls = c === '全部' && currentCategory === 'all' ? 'active' : 
                 c === currentCategory ? 'active' : '';
    const val = c === '全部' ? 'all' : c;
    return `<button class="section-tab ${cls}" data-cat="${val}">${c}</button>`;
  }).join('');
}

// ── Filter & Sort ──────────────────────────────────────────────────────────────
function getFilteredCourses() {
  let filtered = [...courses];

  // Category
  if (currentCategory !== 'all') {
    filtered = filtered.filter(c => c.category === currentCategory);
  }

  // Search
  if (searchTerm) {
    const q = searchTerm.toLowerCase();
    filtered = filtered.filter(c =>
      c.title.toLowerCase().includes(q) ||
      c.desc.toLowerCase().includes(q) ||
      c.tags.some(t => t.toLowerCase().includes(q))
    );
  }

  // Sort
  if (currentSort === 'latest') {
    // by id desc (newer first)
    filtered.sort((a, b) => b.id.localeCompare(a.id));
  } else if (currentSort === 'progress') {
    filtered.sort((a, b) => b.progress - a.progress);
  } else if (currentSort === 'name') {
    filtered.sort((a, b) => a.title.localeCompare(b.title, 'zh'));
  }

  return filtered;
}

// ── Render Courses ─────────────────────────────────────────────────────────────
function renderCourses() {
  const filtered = getFilteredCourses();
  const grid = document.getElementById('courseList');
  const tpl = document.getElementById('courseCardTpl');

  grid.innerHTML = '';

  filtered.forEach(course => {
    const card = tpl.content.cloneNode(true);
    const article = card.querySelector('.course-card');
    article.onclick = () => window.location.href = course.url;

    // Badge
    const badge = card.querySelector('#badge');
    badge.textContent = 
      course.status === 'completed' ? '已完成' :
      course.status === 'in-progress' ? '进行中' : '未开始';
    badge.className = 'course-card-badge ' +
      (course.status === 'completed' ? 'badge-completed' :
       course.status === 'in-progress' ? 'badge-in-progress' : 'badge-not-started');

    // Title & desc
    card.querySelector('.course-card-title').textContent = course.title;
    card.querySelector('.course-card-desc').textContent = course.desc;

    // Meta
    card.querySelector('.course-card-lessons').textContent = `${course.lessons} 课时`;
    card.querySelector('.course-card-time').textContent = course.time;

    // Progress
    card.querySelector('#progressFill').style.width = `${course.progress}%`;
    card.querySelector('#progressText').textContent = `${course.progress}%`;

    // Tags
    const tagsWrap = card.querySelector('#tags');
    course.tags.forEach(t => {
      const span = document.createElement('span');
      span.className = 'course-tag';
      span.textContent = t;
      tagsWrap.appendChild(span);
    });

    grid.appendChild(card);
  });

  document.getElementById('resultCount').textContent = `${filtered.length} 门`;
  document.getElementById('stickySummaryText').textContent =
    searchTerm ? `搜索"${searchTerm}" — ${filtered.length} 门课` :
    currentCategory === 'all' ? `全部 ${courses.length} 门课程` :
    `${currentCategory} — ${filtered.length} 门课程`;
}

// ── Render Progress ────────────────────────────────────────────────────────────
function renderProgress() {
  const wrap = document.getElementById('progressBars');
  const inProgressCourses = courses.filter(c => c.status === 'in-progress' || c.status === 'not-started');

  if (inProgressCourses.length === 0) {
    wrap.innerHTML = '<p style="color:var(--text-light);font-size:14px;">暂无进行中的课程</p>';
    return;
  }

  wrap.innerHTML = inProgressCourses.map(c => `
    <div class="progress-item">
      <span class="progress-item-name">${c.title}</span>
      <div class="progress-item-bar">
        <div class="progress-item-fill" style="width:${c.progress}%"></div>
      </div>
      <span class="progress-item-text">${c.progress}%</span>
    </div>
  `).join('');
}

// ── Events ─────────────────────────────────────────────────────────────────────
function bindEvents() {
  // Search
  document.getElementById('searchInput').addEventListener('input', e => {
    searchTerm = e.target.value;
    renderCourses();
  });

  // Category tabs
  document.getElementById('categoryTabs').addEventListener('click', e => {
    if (!e.target.classList.contains('section-tab')) return;
    currentCategory = e.target.dataset.cat;
    renderCategoryTabs();
    renderCourses();
  });

  // Sort buttons
  document.querySelectorAll('.list-sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.list-sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentSort = btn.dataset.sort;
      renderCourses();
    });
  });
}

// ── Boot ────────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
