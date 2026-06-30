// Teach Platform - app-generate.js
// 首页：输入主题 → 触发生成（本地 API 模式）

const API_BASE = 'http://localhost:5000';  // 本地 API 服务器

let currentTask = null;  // 当前生成任务
let pollInterval = null;  // 轮询定时器

// ── 初始化 ───────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadRecentCourses();
  checkURLForStatus();
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
  
  // 重置进度显示
  document.getElementById('progressSteps').innerHTML = '';
  document.getElementById('progressBar').style.width = '0%';
  document.getElementById('progressLog').textContent = '正在提交任务...';

  try {
    // 调用本地 API
    const resp = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.error || '提交失败');
    }

    const data = await resp.json();
    currentTask = data.task_id;
    
    updateLog(`任务已创建（ID: ${currentTask}），开始生成...`);
    updateProgress(0, '提交任务');
    
    // 开始轮询进度
    startPolling(currentTask, topic);
    
  } catch (err) {
    updateLog(`提交失败：${err.message}`);
    resetButton();
    
    // 如果 API 服务器未启动，提示用户
    if (err.message.includes('fetch')) {
      updateLog('⚠️ 请确保 API 服务器已启动（运行 python api_server.py）');
    }
  }
}

// ── 轮询任务进度 ───────────────────────────────────────────────────────────
function startPolling(taskId, topic) {
  if (pollInterval) clearInterval(pollInterval);
  
  let attempts = 0;
  const maxAttempts = 120;  // 最多等 10 分钟（每 5 秒一次）
  
  pollInterval = setInterval(async () => {
    attempts++;
    
    try {
      const resp = await fetch(`${API_BASE}/api/status/${taskId}`);
      if (!resp.ok) return;
      
      const task = await resp.json();
      
      // 更新进度
      updateProgress(task.progress, task.steps[task.steps.length - 1]?.message || '');
      
      // 检查是否完成
      if (task.status === 'done') {
        clearInterval(pollInterval);
        updateProgress(100, '课程生成完成！');
        updateLog(`✅ 课程已生成！<a href="library.html">查看课程库</a>`);
        
        // 刷新课程列表
        loadRecentCourses();
        resetButton();
        
      } else if (task.status === 'error') {
        clearInterval(pollInterval);
        updateLog(`❌ 生成失败：${task.error}`);
        resetButton();
      }
      
    } catch (e) {
      console.error('轮询错误:', e);
    }
    
    // 超时
    if (attempts > maxAttempts) {
      clearInterval(pollInterval);
      updateLog('⚠️ 生成超时，请检查服务器状态');
      resetButton();
    }
    
  }, 5000);  // 每 5 秒轮询一次
}

// ── 更新进度显示 ────────────────────────────────────────────────────────────
function updateProgress(pct, message) {
  const barEl = document.getElementById('progressBar');
  const logEl = document.getElementById('progressLog');
  
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
  const stepsEl = document.getElementById('progressSteps');
  
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
  
  // 更新日志
  if (message && logEl) {
    logEl.textContent = message;
  }
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
    const resp = await fetch(`${API_BASE}/api/courses?t=${Date.now()}`);
    if (!resp.ok) return;
    const data = await resp.json();
    const courses = (data.courses || []).slice(0, 6);
    renderCourseCards(courses);
  } catch (e) {
    console.log('加载课程失败:', e);
    // 如果 API 未启动，尝试直接读取本地文件
    try {
      const resp2 = await fetch(`data/courses.json?t=${Date.now()}`);
      if (resp2.ok) {
        const data2 = await resp2.json();
        renderCourseCards((data2.courses || []).slice(0, 6));
      }
    } catch (e2) {
      console.log('暂无课程数据');
    }
  }
}

function renderCourseCards(courses) {
  const grid = document.getElementById('recentCourses');
  if (!courses.length) {
    grid.innerHTML = '<div id="emptyState" style="text-align:center;padding:40px;color:#999;">暂无课程，输入主题开始生成吧！</div>';
    return;
  }

  document.getElementById('emptyState')?.remove();

  let html = '';
  courses.forEach(c => {
    const progress = c.progress || 0;
    html += `<div class="course-card" onclick="location.href='lesson.html?course=${c.id}'">
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

// ── URL 参数检查 ──────────────────────────────────────────────────────────
function checkURLForStatus() {
  const params = new URLSearchParams(location.search);
  if (params.get('generated')) {
    updateLog('课程生成完成！已添加到课程库。');
  }
}
