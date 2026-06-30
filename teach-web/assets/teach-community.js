/**
 * teach-community.js — 社区讨论模块（基于 GitHub Issues）
 * 
 * 功能:
 * 1. 显示课程相关讨论（从 GitHub Issues 加载）
 * 2. 发起新讨论（跳转 GitHub Issue 创建页）
 * 3. 点赞/投票（GitHub Reactions）
 * 
 * 配置: 在 teach-web 的 index.html 中设置 window.TEACH_COMMUNITY_CONFIG
 *   window.TEACH_COMMUNITY_CONFIG = {
 *     repo: 'normanwang929/teach',  // GitHub 仓库
 *     apiUrl: 'https://api.github.com/repos/normanwang929/teach/issues',
 *   };
 */

(function () {
  'use strict';

  const DEFAULT_CONFIG = {
    repo: '',       // 必需: 'username/repo'
    apiUrl: '',     // 自动构建
    enablePost: true,
  };

  function getConfig() {
    const userConfig = window.TEACH_COMMUNITY_CONFIG || {};
    const config = { ...DEFAULT_CONFIG, ...userConfig };
    if (!config.apiUrl && config.repo) {
      config.apiUrl = `https://api.github.com/repos/${config.repo}/issues`;
    }
    return config;
  }

  // ── 加载讨论列表 ───────────────────────────────────────────
  async function loadDiscussions(container, courseId, options = {}) {
    const config = getConfig();
    if (!config.repo) {
      container.innerHTML = '<p class="community-empty">⚠️ 未配置社区仓库，请在 index.html 中设置 TEACH_COMMUNITY_CONFIG.repo</p>';
      return;
    }

    container.innerHTML = '<div class="community-loading">加载讨论中...</div>';

    try {
      // 搜索带有课程标签的 Issue
      const label = options.label || courseId;
      const url = `https://api.github.com/repos/${config.repo}/issues?labels=${encodeURIComponent(label)}&state=open&per_page=20`;

      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const issues = await resp.json();
      renderDiscussions(container, issues, courseId);
    } catch (err) {
      container.innerHTML = `
        <div class="community-empty">
          <p>📭 暂无讨论</p>
          <p class="community-hint">成为第一个发起讨论的人吧！</p>
          <button class="btn-new-discussion" onclick="TeachCommunity.newDiscussion('${courseId}')">
            ✏️ 发起新讨论
          </button>
        </div>`;
    }
  }

  // ── 渲染讨论列表 ───────────────────────────────────────────
  function renderDiscussions(container, issues, courseId) {
    if (!issues || issues.length === 0) {
      container.innerHTML = `
        <div class="community-empty">
          <p>📭 暂无讨论</p>
          <p class="community-hint">成为第一个发起讨论的人吧！</p>
          <button class="btn-new-discussion" onclick="TeachCommunity.newDiscussion('${courseId}')">
            ✏️ 发起新讨论
          </button>
        </div>`;
      return;
    }

    let html = `<div class="community-list">`;
    html += `<div class="community-header">`;
    html += `<h3>💬 课程讨论</h3>`;
    html += `<button class="btn-new-discussion" onclick="TeachCommunity.newDiscussion('${courseId}')">✏️ 发起新讨论</button>`;
    html += `</div>`;

    issues.forEach(issue => {
      const createdAt = new Date(issue.created_at).toLocaleDateString('zh-CN');
      html += `<div class="community-item">`;
      html += `<div class="community-item-header">`;
      html += `<a href="${issue.html_url}" target="_blank" class="community-item-title">${escapeHtml(issue.title)}</a>`;
      html += `</div>`;
      html += `<div class="community-item-meta">`;
      html += `<span class="community-author">👤 ${escapeHtml(issue.user.login)}</span>`;
      html += `<span class="community-date">📅 ${createdAt}</span>`;
      html += `<span class="community-comments">💬 ${issue.comments} 条评论</span>`;
      html += `</div>`;
      if (issue.body) {
        const preview = issue.body.length > 200 ? issue.body.slice(0, 200) + '...' : issue.body;
        html += `<div class="community-item-body">${escapeHtml(preview)}</div>`;
      }
      html += `</div>`;
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  // ── 发起新讨论 ─────────────────────────────────────────────
  function newDiscussion(courseId, title = '') {
    const config = getConfig();
    if (!config.repo) {
      alert('⚠️ 未配置社区仓库');
      return;
    }

    const defaultTitle = title || `[${courseId}] 讨论`;
    const url = `https://github.com/${config.repo}/issues/new?title=${encodeURIComponent(defaultTitle)}&labels=${encodeURIComponent(courseId)}`;
    window.open(url, '_blank');
  }

  // ── 工具函数 ───────────────────────────────────────────────
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ── 导出 API ───────────────────────────────────────────────
  window.TeachCommunity = {
    load: loadDiscussions,
    new: newDiscussion,
    config: getConfig,
  };

})();
