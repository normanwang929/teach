> 本课程专为编程初学者和希望系统学习 Git 的开发者设计。通过 1-2 小时的学习，你将掌握 Git 的核心概念、基本操作和常用工作流程。课程采用理论与实践结合的方式，包含丰富的代码示例和操作演示，帮助你从零开始建立对版本控制系统的深刻理解。建议在学习过程中打开终端，跟随课程内容同步操作，以获得最佳学习效果。参考资源包括《Pro Git》中文版、菜鸟教程和 Learn Git Branching 互动学习平台。

## 第一章 Git 概述与安装

### 1.1 什么是版本控制

**学习目标：**
- 理解版本控制的基本概念和重要性
- 区分集中式和分布式版本控制系统的区别
- 了解 Git 的历史和设计理念

**讲义：**

版本控制是软件开发中不可或缺的基础设施。想象一下，当你撰写一份重要文档时，可能会保存多个版本，如“论文初稿.docx”、“论文修改版.docx”、“论文最终版.docx”，甚至“论文最终版2.docx”。这种方式不仅混乱，而且难以追溯修改历史，更无法多人协作。版本控制系统正是为解决这些问题而生。

版本控制系统（VCS）的核心功能包括：

1. **历史追溯**：记录文件的每一次修改，包括谁在什么时间修改了哪些内容。这就像为你的项目建立了一台“时间机器”，可以随时回到任何一个历史状态。

2. **协作支持**：允许多人同时修改同一个项目，系统会自动合并或提示冲突。想象一下，一个团队有10个人同时开发同一个功能，如果没有版本控制，管理代码的合并将是灾难性的。

3. **分支管理**：可以创建独立的开发分支，在不影响主线代码的情况下进行实验性开发。当功能稳定后再合并回主分支。

4. **备份与恢复**：代码的所有历史版本都存储在仓库中，即使本地文件损坏，也可以从远程仓库恢复。

Git 与其他版本控制系统的核心区别在于分布式架构。传统的集中式版本控制系统（如 SVN）有一个中央服务器，所有操作都需要联网。而 Git 是分布式的，每个开发者本地都拥有完整的代码仓库副本，即使没有网络也可以进行大部分操作，只在需要同步时才连接远程仓库。

Git 由 Linux 创始人 Linus Torvalds 于 2005 年创建，最初是为了管理 Linux 内核的开发。它的设计目标是：速度、简单设计、对非线性开发（分支）的强力支持、完全分布式、能够高效处理大型项目。如今，Git 已成为全球最流行的版本控制系统，被数百万开发者和几乎所有科技公司使用。

### 1.2 安装与配置 Git

**学习目标：**
- 在不同操作系统上安装 Git
- 完成 Git 的初始配置
- 验证安装是否成功

**讲义：**

Git 的安装过程因操作系统而异，但都非常简单。以下是各平台的安装方法：

**Windows 用户**：
访问 Git 官方网站（https://git-scm.com/download/win）下载安装程序，运行后一路默认选项即可。安装完成后，你会在开始菜单中找到 Git Bash，这是一个模拟 Linux 环境的终端。

**macOS 用户**：
最简单的方式是安装 Xcode Command Line Tools，在终端中运行：
```bash
xcode-select --install
```
或者使用 Homebrew 安装：
```bash
brew install git
```

**Linux 用户**：
不同发行版的安装命令略有不同：
- Ubuntu/Debian: `sudo apt-get install git`
- CentOS/Fedora: `sudo yum install git`
- Arch Linux: `sudo pacman -S git`

安装完成后，打开终端（Windows 用户使用 Git Bash），输入以下命令验证安装：
```bash
git --version
```
如果显示类似 `git version 2.39.0` 的版本信息，说明安装成功。

接下来进行初始配置，这是使用 Git 前必须完成的步骤。Git 需要知道你是谁，因为每次提交都会记录作者信息：
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```
`--global` 参数表示全局配置，对所有 Git 仓库生效。你也可以在特定仓库中使用 `--local` 参数覆盖全局设置。

其他常用配置：
```bash
# 设置默认编辑器为 VS Code
git config --global core.editor "code --wait"

# 设置换行符自动转换（Windows 用户推荐）
git config --global core.autocrlf true

# 查看所有配置
git config --list
```

## 第二章 Git 基础操作

### 2.1 创建仓库与首次提交

**学习目标：**
- 学会创建 Git 仓库的两种方式
- 理解工作区、暂存区和仓库的概念
- 完成第一次代码提交

**讲义：**

创建 Git 仓库有两种方式：初始化新仓库和克隆已有仓库。我们先学习第一种方式。

**初始化新仓库**：
在项目文件夹中打开终端，运行：
```bash
mkdir my-first-repo
cd my-first-repo
git init
```
`git init` 命令会在当前目录创建一个名为 `.git` 的隐藏文件夹，这就是 Git 仓库的核心。所有版本信息都存储在这里。注意：千万不要手动修改 `.git` 文件夹的内容，否则可能导致仓库损坏。

**文件状态与三区域模型**：
Git 将文件分为三种状态，对应三个工作区域：

1. **工作区（Working Directory）**：你实际编辑文件的地方，就是项目文件夹。
2. **暂存区（Staging Area）**：一个临时存储区域，用于准备下一次提交的内容。
3. **仓库（Repository）**：Git 用来保存项目元数据和对象数据库的地方，即 `.git` 文件夹。

文件在 Git 中的生命周期如下：
- **未跟踪（Untracked）**：新创建的文件，Git 还不知道它的存在。
- **已暂存（Staged）**：文件被添加到暂存区，准备提交。
- **已提交（Committed）**：文件被安全地保存在本地仓库中。

**首次提交实战**：
创建一个简单的 HTML 文件：
```bash
echo "<h1>Hello Git!</h1>" > index.html
```
现在查看仓库状态：
```bash
git status
```
你会看到 `index.html` 显示为未跟踪的红色文件。接下来将它添加到暂存区：
```bash
git add index.html
```
再次运行 `git status`，文件变为绿色，表示已暂存。最后提交：
```bash
git commit -m "初始化项目，添加 index.html"
```
`-m` 参数后面跟提交信息，用来描述这次提交做了什么。好的提交信息应该简洁明了，如“修复登录按钮的样式错误”而不是简单的“修改”。

如果想一次性添加所有文件到暂存区，可以使用：
```bash
git add .
```
但要注意，这可能会添加你不想跟踪的文件（如编译产物、日志文件等）。我们将在后续章节学习如何处理这些文件。

### 2.2 查看历史与版本回退

**学习目标：**
- 查看提交历史记录
- 理解 Git 的版本回退机制
- 学会使用 `git log` 和 `git reset`

**讲义：**

**查看提交历史**：
`git log` 是最常用的历史查看命令。默认情况下，它会按时间倒序显示所有提交：
```bash
git log
```
输出格式如下：
```
commit 9d3f2e1a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2 (HEAD -> master)
Author: Your Name <email@example.com>
Date:   Mon Jan 1 12:00:00 2024 +0800

    初始化项目，添加 index.html
```
每个提交都有一个唯一的 SHA-1 哈希值（如 `9d3f2e1...`），用于标识这个提交。`HEAD` 指针指向当前所在的分支和提交。

常用参数：
```bash
# 显示简洁的一行格式
git log --oneline

# 显示图形化的分支历史
git log --graph --oneline --all

# 显示最近的3条提交
git log -3
```

**版本回退**：
Git 允许你回到任何一个历史版本。假设我们连续提交了三次，现在想回到第二次提交的状态。

首先，使用 `git log` 找到目标提交的哈希值。然后使用 `git reset` 命令：
```bash
# --soft：只移动 HEAD 指针，工作区和暂存区不变
git reset --soft <commit-hash>

# --mixed（默认）：移动 HEAD 指针，重置暂存区，工作区不变
git reset --mixed <commit-hash>

# --hard：移动 HEAD 指针，重置暂存区和工作区（危险！会丢失未提交的修改）
git reset --hard <commit-hash>
```
**重要警告**：`--hard` 参数会永久删除工作区的所有未提交修改，使用前请三思。如果只是想撤销暂存区的文件，可以使用：
```bash
git reset HEAD <file>
```
这相当于 `git add` 的反向操作，将文件从暂存区移回工作区。

**回到未来**：
如果回退后想回到最新的版本，但 `git log` 已经看不到那个提交了，可以使用 `git reflog`：
```bash
git reflog
```
这个命令记录了所有 HEAD 指针的移动历史，包括回退操作。找到目标提交的哈希值后，再用 `git reset` 跳转回去。

## 第三章 分支管理

### 3.1 分支的概念与创建

**学习目标：**
- 理解 Git 分支的工作原理
- 学会创建和切换分支
- 掌握分支合并的基本操作

**讲义：**

**什么是分支**：
分支是 Git 最强大的功能之一。简单来说，分支就是指向某个提交的指针。当你创建新分支时，Git 只是创建了一个新的可移动指针。

想象一下，你正在开发一个电商网站的主线功能，突然需要紧急修复一个线上 bug。你可以在主分支上创建一个修复分支，在修复分支上工作，修复完成后合并回主分支。这样既不影响主线开发，又能快速修复问题。

**创建和切换分支**：
```bash
# 创建新分支
git branch feature-login

# 查看所有分支（* 表示当前所在分支）
git branch

# 切换到指定分支
git checkout feature-login

# 创建并切换分支（一步到位）
git checkout -b feature-login
```
从 Git 2.23 版本开始，推荐使用更语义化的 `switch` 命令：
```bash
# 切换分支
git switch feature-login

# 创建并切换
git switch -c feature-login
```

**分支合并**：
假设我们在 `feature-login` 分支上完成了一个功能，现在要合并回 `master` 主分支：
```bash
# 先切换到目标分支（接收合并的分支）
git checkout master

# 执行合并
git merge feature-login
```
Git 会自动进行“三方合并”，如果两个分支没有冲突，合并会顺利完成。合并后，`master` 分支就包含了 `feature-login` 的所有修改。

**删除分支**：
合并完成后，可以删除不再需要的分支：
```bash
# 删除本地分支
git branch -d feature-login

# 强制删除（分支未合并时使用）
git branch -D feature-login
```

### 3.2 解决合并冲突

**学习目标：**
- 理解合并冲突产生的原因
- 学会手动解决冲突
- 掌握冲突解决后的提交流程

**讲义：**

**冲突的产生**：
当两个分支修改了同一个文件的同一行代码时，Git 无法自动决定保留哪个版本，就会产生冲突。这是版本控制中最常见也最需要谨慎处理的情况。

**模拟冲突**：
1. 在 `master` 分支上创建文件 `app.js`，内容为：
```javascript
function greet() {
    console.log("Hello");
}
```
提交这个文件。

2. 创建并切换到 `feature` 分支，修改 `app.js` 中 `greet` 函数为：
```javascript
function greet() {
    console.log("Hi from feature");
}
```
提交修改。

3. 切回 `master` 分支，修改 `app.js` 中 `greet` 函数为：
```javascript
function greet() {
    console.log("Hello from master");
}
```
提交修改。

4. 尝试合并 `feature` 分支到 `master`：
```bash
git merge feature
```
此时 Git 会提示冲突，并显示：
```
Auto-merging app.js
CONFLICT (content): Merge conflict in app.js
Automatic merge failed; fix conflicts and then commit the result.
```

**解决冲突**：
打开冲突文件，你会看到类似这样的内容：
```javascript
function greet() {
<<<<<<< HEAD
    console.log("Hello from master");
=======
    console.log("Hi from feature");
>>>>>>> feature
}
```
`<<<<<<< HEAD` 和 `=======` 之间是当前分支（master）的内容，`=======` 和 `>>>>>>> feature` 之间是合并进来的分支（feature）的内容。

你需要手动编辑文件，决定保留哪个版本或重新编写：
```javascript
function greet() {
    console.log("Hello from master with feature enhancement");
}
```
删除冲突标记后，保存文件。然后：
```bash
# 标记冲突已解决
git add app.js

# 完成合并提交
git commit -m "解决 app.js 合并冲突"
```

**冲突预防技巧**：
1. 经常拉取远程仓库的最新代码，保持分支同步。
2. 在合并前，先切换到目标分支并拉取最新代码。
3. 使用 `git diff` 预览将要合并的更改。
4. 保持提交粒度小，功能单一，这样冲突范围更可控。

## 第四章 远程仓库与协作

### 4.1 连接远程仓库

**学习目标：**
- 理解远程仓库的概念
- 学会使用 GitHub/GitLab 创建远程仓库
- 掌握 `git remote` 相关操作

**讲义：**

**什么是远程仓库**：
远程仓库是托管在互联网（如 GitHub、GitLab、Gitee）或内网服务器上的 Git 仓库副本。它作为团队协作的中心枢纽，允许开发者推送和拉取代码。

**创建远程仓库**：
以 GitHub 为例：
1. 登录 GitHub，点击右上角的 "+" 号，选择 "New repository"。
2. 填写仓库名称（如 `my-project`），选择公开或私有。
3. 不要勾选 "Initialize this repository with a README"（因为我们已经有本地仓库）。
4. 点击 "Create repository"。

**关联本地与远程仓库**：
在本地仓库中执行：
```bash
# 添加远程仓库（origin 是远程仓库的默认名称）
git remote add origin https://github.com/your-username/my-project.git

# 查看远程仓库信息
git remote -v

# 推送本地 master 分支到远程
git push -u origin master
```
`-u` 参数（`--set-upstream`）会将本地分支与远程分支关联，之后可以直接使用 `git push` 和 `git pull` 而不需要指定远程仓库和分支。

**克隆远程仓库**：
如果项目已经存在于远程仓库，你可以克隆到本地：
```bash
git clone https://github.com/other-user/awesome-project.git
```
这会自动完成以下操作：
- 初始化本地仓库
- 添加远程仓库（默认名为 origin）
- 下载所有分支和历史记录
- 自动切换到主分支

**远程仓库操作命令**：
```bash
# 从远程拉取最新数据（但不自动合并）
git fetch origin

# 拉取并自动合并到当前分支
git pull origin master

# 推送所有分支到远程
git push --all origin

# 删除远程分支
git push origin --delete feature-old
```

### 4.2 团队协作工作流

**学习目标：**
- 掌握基于分支的协作流程
- 学会处理推送冲突
- 理解 Pull Request 的概念

**讲义：**

**典型协作流程**：
假设你和同事 Alice 共同开发一个项目，采用 Feature Branch 工作流：

1. **同步主分支**：
```bash
git checkout master
git pull origin master
```

2. **创建功能分支**：
```bash
git checkout -b feature-user-profile
```

3. **开发并提交**：
```bash
# 修改文件...
git add .
git commit -m "添加用户头像功能"
```

4. **推送分支到远程**：
```bash
git push -u origin feature-user-profile
```

5. **创建 Pull Request**：
在 GitHub 上发起 Pull Request（PR），请求将你的分支合并到 master。团队成员可以审查代码、提出修改建议。

6. **处理审查意见**：
在本地分支上继续修改并提交，推送后 PR 会自动更新。

7. **合并到主分支**：
审查通过后，在 GitHub 上点击 "Merge pull request"。

**处理推送冲突**：
当你在推送时，如果远程仓库有新的提交，Git 会拒绝推送并提示：
```
! [rejected]        master -> master (fetch first)
error: failed to push some refs to '...'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally.
```
解决方法：
```bash
# 拉取远程代码并合并
git pull origin master

# 解决可能的冲突后
git push origin master
```
或者使用更安全的方式：
```bash
# 先 fetch，再 rebase
git fetch origin
git rebase origin/master
git push origin master
```
`rebase` 会将你的提交放在远程提交之后，形成一条直线历史，但需要谨慎使用，因为它会改写提交历史。

**最佳实践**：
1. 每次开始工作前先 `git pull` 同步。
2. 保持分支功能单一，及时合并。
3. 提交信息要清晰描述改动内容。
4. 定期推送，避免本地积累大量未推送的提交。
5. 在合并到主分支前，确保功能完整且经过测试。

## 第五章 进阶技巧与最佳实践

### 5.1 .gitignore 与文件管理

**学习目标：**
- 学会编写 .gitignore 文件
- 理解文件忽略规则
- 掌握管理已跟踪文件的方法

**讲义：**

**.gitignore 的作用**：
在实际项目中，并不是所有文件都需要被 Git 跟踪。例如：
- 编译产物（.class、.exe、.dll）
- 依赖包（node_modules、vendor）
- 环境配置文件（.env、config.local.php）
- 操作系统文件（.DS_Store、Thumbs.db）
- IDE 配置（.idea、.vscode）

`.gitignore` 文件告诉 Git 哪些文件应该被忽略。

**编写规则**：
```gitignore
# 注释以 # 开头

# 忽略特定文件
