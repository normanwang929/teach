/**
 * teach-progress.js — 学习进度跟踪模块
 * 
 * 功能:
 * 1. 记录每门课的学习进度（localStorage）
 * 2. 跨页面同步进度
 * 3. 导出/导入进度（JSON 文件）
 * 4. 生成学习报告
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'teach-progress';
  const RECORDS_KEY = 'teach-learning-records';

  // ── 进度数据结构 ───────────────────────────────────────────
  // progress = {
  //   "python-basics": {
  //     "courseId":   "python-basics",
  //     "title":      "Python 入门",
  //     "startedAt":  "2025-06-01T10:00:00Z",
  //     "lastAccess": "2025-06-30T22:00:00Z",
  //     "percent":    65,
  //     "sections":   { "0": true, "1": true, "2": false },
  //     "quizScore":  80,
  //     "timeSpent":  3600,  // 秒
  //   }
  // }

  // ── 读取/保存 ───────────────────────────────────────────────
  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch {
      return {};
    }
  }

  function saveProgress(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    // 触发跨标签页同步
    window.dispatchEvent(new Event('teach-progress-change'));
  }

  // ── 开始课程 ────────────────────────────────────────────────
  function startCourse(courseId, title) {
    const data = getProgress();
    if (!data[courseId]) {
      data[courseId] = {
        courseId,
        title,
        startedAt: new Date().toISOString(),
        lastAccess: new Date().toISOString(),
        percent: 0,
        sections: {},
        quizScore: null,
        timeSpent: 0,
      };
      saveProgress(data);
    }
    return data[courseId];
  }

  // ── 更新进度 ────────────────────────────────────────────────
  function updateSection(courseId, sectionIndex, completed = true) {
    const data = getProgress();
    if (!data[courseId]) return;

    data[courseId].sections[sectionIndex] = completed;
    data[courseId].lastAccess = new Date().toISOString();

    // 计算百分比
    const sections = data[courseId].sections;
    const total = Object.keys(sections).length;
    const done = Object.values(sections).filter(Boolean).length;
    data[courseId].percent = total > 0 ? Math.round(done / total * 100) : 0;

    saveProgress(data);
  }

  function updateQuizScore(courseId, score) {
    const data = getProgress();
    if (!data[courseId]) return;
    data[courseId].quizScore = score;
    data[courseId].lastAccess = new Date().toISOString();
    saveProgress(data);
  }

  function addTimeSpent(courseId, seconds) {
    const data = getProgress();
    if (!data[courseId]) return;
    data[courseId].timeSpent = (data[courseId].timeSpent || 0) + seconds;
    saveProgress(data);
  }

  // ── 获取单课程进度 ─────────────────────────────────────────
  function getCourseProgress(courseId) {
    return getProgress()[courseId] || null;
  }

  // ── 获取所有进度（用于首页展示）────────────────────────────
  function getAllProgress() {
    return getProgress();
  }

  // ── 生成学习报告 ────────────────────────────────────────────
  function generateReport() {
    const data = getProgress();
    const courses = Object.values(data);

    const totalCourses = courses.length;
    const completedCourses = courses.filter(c => c.percent >= 100).length;
    const inProgressCourses = courses.filter(c => c.percent > 0 && c.percent < 100).length;
    const totalTimeSpent = courses.reduce((sum, c) => sum + (c.timeSpent || 0), 0);

    return {
      totalCourses,
      completedCourses,
      inProgressCourses,
      totalTimeSpent,
      totalTimeSpentStr: formatTime(totalTimeSpent),
      courses: courses.sort((a, b) => new Date(b.lastAccess) - new Date(a.lastAccess)),
    };
  }

  function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (h > 0) return `${h} 小时 ${m} 分钟`;
    return `${m} 分钟`;
  }

  // ── 导出进度 ────────────────────────────────────────────────
  function exportProgress() {
    const data = getProgress();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `teach-progress-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── 导入进度 ────────────────────────────────────────────────
  function importProgress(file, merge = true) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = function (e) {
        try {
          const imported = JSON.parse(e.target.result);
          if (merge) {
            const current = getProgress();
            const merged = { ...current, ...imported };
            saveProgress(merged);
          } else {
            saveProgress(imported);
          }
          resolve(true);
        } catch (err) {
          reject(err);
        }
      };
      reader.readAsText(file);
    });
  }

  // ── 渲染进度条 ──────────────────────────────────────────────
  function renderProgressBar(container, courseId) {
    const prog = getCourseProgress(courseId);
    const pct = prog ? prog.percent : 0;

    let html = `<div class="progress-bar-container">`;
    html += `<div class="progress-bar" style="width: ${pct}%"></div>`;
    html += `<span class="progress-label">${pct}%</span>`;
    html += `</div>`;
    container.innerHTML = html;
  }

  // ── 跨标签页同步 ────────────────────────────────────────────
  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEY) {
      window.dispatchEvent(new Event('teach-progress-sync'));
    }
  });

  // ── 导出 API ────────────────────────────────────────────────
  window.TeachProgress = {
    startCourse,
    updateSection,
    updateQuizScore,
    addTimeSpent,
    getCourseProgress,
    getAllProgress,
    generateReport,
    exportProgress,
    importProgress,
    renderProgressBar,
  };

})();
