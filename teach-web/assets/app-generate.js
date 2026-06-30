// Teach Platform - app-generate.js
// 首页：输入主题 → 触发生成

const GITHUB = {
  owner: 'normanwang929',
  repo:  'teach',
  // 自动检测：如果在 teach 仓库里就用实际值，否则用演示模式
  apiBase: 'https://api.github.com/repos/normanwang929/teach',
};

let currentTask = null;  // 当前生成任务

// ── 初始化 ───────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadRecentCourses();
  checkURlForStatus();
});

// ── 热门标签点击 ─────────────────────────────────────────────────────────────
function setTopic(topic) {
  const input = document.getElementById('topicInput');
  input.value = topic;
  input.focus();
}

// ── 开始生成 ─────────────────────────────────────────────────────────────────
async function startGenerate() {
  const input = document.getElementById('topicInput');
  const topic = input.value.trim();
  if (!topic) { input.focus(); return; }

  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  btn.querySelector('.btn-text').style.display = 'none';
  btn.querySelector('.btn-loading').style.display = 'inline';

  // 显示进度区
  const progressArea = document.getElementById('progressArea');
  progressArea.style.display = 'block';
  updateProgress('提交任务', 'active', 0);

  try {
    // 方案：创建 GitHub Issue 触发生成
    const issueUrl = await submitGenerationTask(topic);
    updateProgress('任务已提交', 'done', 10);
    updateProgress('等待 GitHub Actions 处理…', 'active', 10);
    updateLog(`任务已创建：<a href="${issueUrl}" target="_blank">查看进度</a>`);

    // 开始轮询课程列表，等待新课程出现
    currentTask = { topic, issueUrl, startTime: Date.now() };
    pollForNewCourse(topic);
  } catch (err) {
    updateLog(`提交失败：${err.message}`);
    resetButton();
  }
}

// ── 提交生成任务（创建 GitHub Issue） ─────────────────────────────────────
async function submitGenerationTask(topic) {
  const token = await getGitHubToken();

  if (!token) {
    // 演示模式：不真正创建 Issue，模拟进度
    return simulateGeneration(topic);
  }

  const body = `## 课程生成请求

**主题：** ${topic}

由 Teach 平台自动提交，GitHub Actions 将自动：
1. 搜索学习资料
2. 生成课程大纲和内容
3. 生成播客音频
4. 生成教学视频
5. 提交到课程库

cc @normanwang929`;

  const resp = await fetch(`${GITHUB.apiBase}/issues`, {
    method: 'POST',
    headers: {
      'Authorization': `token ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: `生成课程：${topic}`,
      body: body,
      labels: ['course-generation', 'auto'],
    }),
  });

  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.message || '创建任务失败');
  }

  const issue = await resp.json();
  return issue.html_url;
}

// ── 演示模式：模拟生成进度 ─────────────────────────────────────────────────
function simulateGeneration(topic) {
  return new Promise((resolve) => {
    const steps = [
      ['搜索学习资料…', 20],
      ['找到 12 个相关资料', 35],
      ['生成课程大纲…', 50],
      ['生成讲义内容…', 65],
      ['生成播客音频…', 80],
      ['生成教学视频…', 90],
      ['课程生成完成！', 100],
    ];

    let i = 0;
    const iv = setInterval(() => {
      const [text, pct] = steps[i];
      if (i < steps.length - 1) {
        updateProgress(text, 'active', pct);
      } else {
        updateProgress(text, 'done', pct);
        clearInterval(iv);
        // 添加到最近课程
        addCourseCard({
          id: 'demo-' + Date.now(),
          title: topic,
          description: `关于「${topic}」的自动生成课程`,
          icon: '📚',
          progress: 0,
          tags: ['自动生成'],
          created_at: new Date().toISOString(),
        });
        updateLog('演示模式：实际部署后，课程将自动出现在课程库。');
        resetButton();
        resolve('#demo');
      }
      i++;
    }, 1200);
  });
}

// ── 轮询：等待新课程出现 ───────────────────────────────────────────────────
function pollForNewCourse(topic) {
  let attempts = 0;
  const maxAttempts = 60;  // 最多等 10 分钟（每 10 秒一次）

  const iv = setInterval(async () => {
    attempts++;
    if (attempts > maxAttempts) {
      clearInterval(iv);
      updateLog('生成超时，请到 GitHub Issues 查看任务状态。');
      resetButton();
      return;
    }

    try {
      const resp = await fetch(`${GITHUB.apiBase}/contents/data/courses.json?t=${Date.now()}`);
      if (resp.ok) {
        const data = await resp.json();
        const content = JSON.parse(atob(data.content.replace(/\n/g, '')));
        // 检查是否有匹配的课程
        const found = content.courses?.find(c =>
          c.title.includes(topic) || topic.includes(c.title)
        );
        if (found) {
          clearInterval(iv);
          updateProgress('课程生成完成！', 'done', 100);
          updateLog(`课程已就绪：<a href="library.html?course=${found.id}">开始学习</a>`);
          loadRecentCourses();
          resetButton();
        }
      }
    } catch (e) {
      // 忽略轮询错误
    }

    updateLog(`等待生成完成…（${attempts}/${maxAttempts}）`);
  }, 10000);  // 每 10 秒轮询一次
}

// ── 更新进度显示 ────────────────────────────────────────────────────────────
function updateProgress(text, state, pct) {
  const stepsEl = document.getElementById('progressSteps');
  const barEl = document.getElementById('progressBar');

  // 更新进度条
  if (barEl) barEl.style.width = pct + '%';

  // 更新步骤列表
  const stepNames = [
    '提交任务',
    '搜索资料',
    '生成大纲',
    '生成内容',
    '生成音频',
    '生成视频',
    '完成',
  ];

  const currentIdx = Math.floor(pct / (100 / (stepNames.length - 1)));

  let html = '';
  stepNames.forEach((name, idx) => {
    let cls = 'todo';
    if (idx < currentIdx) cls = 'done';
    else if (idx === currentIdx) cls = 'active';
    const icon = cls === 'done' ? '✓' : (idx + 1);
    html += `<div class="progress-step ${cls}">
      <span class="step-icon">${icon}</span>
      <span>${name}</span>
    </div>`;
  });
  stepsEl.innerHTML = html;
}

function updateLog(msg) {
  const logEl = document.getElementById('progressLog');
  if (logEl) logEl.innerHTML = msg;
}

function resetButton() {
  const btn = document.getElementById('generateBtn');
  btn.disabled = false;
  btn.querySelector('.btn-text').style.display = 'inline';
  btn.querySelector('.btn-loading').style.display = 'none';
}

// ── 加载最近课程 ───────────────────────────────────────────────────────────
async function loadRecentCourses() {
  try {
    const resp = await fetch(`data/courses.json?t=${Date.now()}`);
    if (!resp.ok) return;
    const data = await resp.json();
    const courses = (data.courses || []).slice(0, 6);
    renderCourseCards(courses);
  } catch (e) {
    console.log('暂无课程数据');
  }
}

function renderCourseCards(courses) {
  const grid = document.getElementById('recentCourses');
  if (!courses.length) return;

  document.getElementById('emptyState')?.remove();

  let html = '';
  courses.forEach(c => {
    const progress = c.progress || 0;
    html += `<div class="course-card" onclick="location.href='library.html?course=${c.id}'">
      <div class="course-card-header">${c.icon || '📚'}</div>
      <div class="course-card-body">
        <div class="course-card-title">${c.title}</div>
        <div class="course-card-desc">${c.description || ''}</div>
        <div class="course-card-meta">
          <div class="course-card-tags">
            ${(c.tags || []).slice(0, 2).map(t => `<span class="tag">${t}</span>`).join('')}
          </div>
          <div class="progress-mini">
            <div class="progress-mini-inner" style="width:${progress}%"></div>
          </div>
        </div>
      </div>
    </div>`;
  });
  grid.innerHTML = html;
}

function addCourseCard(course) {
  const grid = document.getElementById('recentCourses');
  document.getElementById('emptyState')?.remove();
  // 重新加载
  loadRecentCourses();
}

// ── GitHub Token 管理 ──────────────────────────────────────────────────────
async function getGitHubToken() {
  // 从 localStorage 读取用户配置的 token（可选）
  return localStorage.getItem('teach_gh_token') || null;
}

function checkURlForStatus() {
  const params = new URLSearchParams(location.search);
  if (params.get('generated')) {
    updateLog('课程生成完成！已添加到课程库。');
  }
}
