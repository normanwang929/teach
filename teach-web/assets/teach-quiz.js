/**
 * teach-quiz.js — 互动测验模块
 * 
 * 用法: 在课程 HTML 中引入此脚本，自动渲染测验卡片
 * 
 * 数据格式 (JSON):
 * [
 *   {
 *     "question": "Python 中哪个关键字用于定义函数？",
 *     "options": ["func", "def", "function", "define"],
 *     "answer": 1,
 *     "explanation": "def 是 Python 中定义函数的关键字，如 def my_func():"
 *   }
 * ]
 */

(function () {
  'use strict';

  // ── 测验状态 ────────────────────────────────────────────────
  const STORAGE_KEY = 'teach-quiz-results';

  function loadResults() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch {
      return {};
    }
  }

  function saveResults(results) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(results));
  }

  // ── 渲染测验卡片 ────────────────────────────────────────────
  function renderQuiz(container, quizData, courseId) {
    const results = loadResults();
    const courseResults = results[courseId] || {};

    let html = `<div class="quiz-container" data-course="${courseId}">`;
    html += `<h3 class="quiz-title">📝 随堂测验</h3>`;
    html += `<div class="quiz-progress">已完成 <span class="quiz-done">0</span> / <span class="quiz-total">${quizData.length}</span> 题</div>`;
    html += `<div class="quiz-cards">`;

    quizData.forEach((q, i) => {
      const answered = courseResults[i] !== undefined;
      const isCorrect = courseResults[i] === q.answer;
      const userAnswer = courseResults[i];

      html += `<div class="quiz-card ${answered ? (isCorrect ? 'correct' : 'wrong') : ''}" data-index="${i}">`;
      html += `<div class="quiz-question">${i + 1}. ${escapeHtml(q.question)}</div>`;
      html += `<div class="quiz-options">`;

      q.options.forEach((opt, j) => {
        let cls = 'quiz-option';
        if (answered) {
          if (j === q.answer) cls += ' correct-option';
          if (j === userAnswer && j !== q.answer) cls += ' wrong-option';
        }
        html += `<div class="${cls}" data-option="${j}">${escapeHtml(opt)}</div>`;
      });

      html += `</div>`; // .quiz-options

      if (answered) {
        html += `<div class="quiz-explanation">💡 ${escapeHtml(q.explanation || '')}</div>`;
      }

      html += `</div>`; // .quiz-card
    });

    html += `</div>`; // .quiz-cards

    // 汇总
    const totalAnswered = Object.keys(courseResults).length;
    const totalCorrect = Object.values(courseResults).filter((a, i) => a === quizData[i]?.answer).length;
    if (totalAnswered === quizData.length) {
      html += `<div class="quiz-summary">`;
      html += `<div class="quiz-score">得分: ${totalCorrect} / ${quizData.length} (${Math.round(totalCorrect / quizData.length * 100)}%)</div>`;
      html += `</div>`;
    }

    html += `</div>`; // .quiz-container

    container.innerHTML = html;

    // 更新进度
    updateProgress(container, totalAnswered, quizData.length);

    // 绑定点击
    container.querySelectorAll('.quiz-option').forEach(el => {
      el.addEventListener('click', function () {
        handleAnswer(container, quizData, courseId, this);
      });
    });
  }

  // ── 处理答题 ────────────────────────────────────────────────
  function handleAnswer(container, quizData, courseId, optionEl) {
    const card = optionEl.closest('.quiz-card');
    if (card.classList.contains('correct') || card.classList.contains('wrong')) return; // 已答

    const qIndex = parseInt(card.dataset.index);
    const selected = parseInt(optionEl.dataset.option);
    const q = quizData[qIndex];
    const isCorrect = selected === q.answer;

    // 保存结果
    const results = loadResults();
    if (!results[courseId]) results[courseId] = {};
    results[courseId][qIndex] = selected;
    saveResults(results);

    // 更新 UI
    card.classList.add(isCorrect ? 'correct' : 'wrong');

    // 标记正确/错误选项
    card.querySelectorAll('.quiz-option').forEach((el, j) => {
      if (j === q.answer) el.classList.add('correct-option');
      if (j === selected && !isCorrect) el.classList.add('wrong-option');
    });

    // 显示解析
    const expEl = document.createElement('div');
    expEl.className = 'quiz-explanation';
    expEl.innerHTML = `💡 ${escapeHtml(q.explanation || '')}`;
    card.querySelector('.quiz-options').after(expEl);

    // 更新进度
    const totalAnswered = Object.keys(results[courseId]).length;
    updateProgress(container, totalAnswered, quizData.length);

    // 全部答完？
    if (totalAnswered === quizData.length) {
      showSummary(container, quizData, courseId, results);
    }
  }

  function updateProgress(container, done, total) {
    const el = container.querySelector('.quiz-done');
    if (el) el.textContent = done;
  }

  function showSummary(container, quizData, courseId, results) {
    const courseResults = results[courseId] || {};
    const totalCorrect = Object.values(courseResults).filter((a, i) => a === quizData[i]?.answer).length;
    const pct = Math.round(totalCorrect / quizData.length * 100);

    let html = `<div class="quiz-summary">`;
    html += `<div class="quiz-score">🎉 测验完成！得分: <strong>${totalCorrect} / ${quizData.length}</strong> (${pct}%)</div>`;
    if (pct >= 80) {
      html += `<div class="quiz-badge">🌟 优秀！你已经掌握了本课内容。</div>`;
    } else if (pct >= 60) {
      html += `<div class="quiz-badge">👍 不错！建议再复习一下错误题目。</div>`;
    } else {
      html += `<div class="quiz-badge">💪 继续加油！建议重新学习本课内容。</div>`;
    }
    html += `</div>`;

    container.querySelector('.quiz-cards').after(html);
  }

  // ── 自动从课程页面加载测验 ─────────────────────────────────
  function autoLoad(courseId) {
    const scriptEl = document.currentScript;
    const containerId = scriptEl?.dataset?.container || 'quiz-container';
    const container = document.getElementById(containerId);
    if (!container) return;

    // 尝试加载同目录下的 quiz.json
    const quizUrl = `./${courseId}-quiz.json`;
    fetch(quizUrl)
      .then(r => r.json())
      .then(data => renderQuiz(container, data, courseId))
      .catch(() => {
        // 没有 quiz.json，不显示测验
        container.style.display = 'none';
      });
  }

  // ── 工具函数 ────────────────────────────────────────────────
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ── 导出 ────────────────────────────────────────────────────
  window.TeachQuiz = {
    render: renderQuiz,
    load: autoLoad,
  };

  // 自动初始化
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-teach-quiz]').forEach(el => {
      const courseId = el.dataset.teachQuiz;
      autoLoad(courseId);
    });
  });

})();
