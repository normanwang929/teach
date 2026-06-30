好的，作为一名资深讲师，我很高兴为您设计这门「Docker 容器技术入门」课程。这份讲义将严格按照您的要求，以 Markdown 格式呈现，结构清晰，内容详实，适合初学者在 1-2 小时内完成学习。

---

> **课程简介：**
>
> 欢迎来到「Docker 容器技术入门」课程。在现代软件开发和运维中，“它在我的机器上可以运行！”这句话常常成为团队协作的噩梦。Docker 正是为此而生。它通过轻量级的容器技术，将应用及其依赖环境打包在一起，实现了“一次构建，随处运行”。
>
> 本课程专为 Docker 零基础的开发者或运维人员设计。我们将从核心概念入手，逐步深入到实际操作。您将学会如何安装 Docker、拉取和运行镜像、构建自定义镜像、管理容器数据，并理解容器与宿主机之间的网络通信。通过本课程的学习，您将能够独立使用 Docker 来部署和运行您的第一个应用，并为后续深入学习容器编排（如 Kubernetes）打下坚实基础。
>
> **课程时长：** 约 1.5 小时
> **前置知识：** 基本的 Linux 命令行操作（如 `cd`, `ls`, `vim`）

---

## 第一章 初识 Docker：为什么我们需要它？

### 1.1 容器 vs. 虚拟机：核心概念辨析

- **学习目标：**
  - 理解传统应用部署方式的痛点。
  - 区分容器与虚拟机在架构上的本质不同。
  - 掌握 Docker 的三大核心组件：镜像、容器、仓库。

- **讲义：**

  欢迎来到第一课。在动手实践之前，我们需要先建立正确的认知框架。想象一下，你开发了一个基于 Python 3.9 和特定库（如 Flask 2.0）的 Web 应用。当你把代码交给同事或部署到服务器时，问题来了：同事的电脑装的是 Python 3.6，服务器是 CentOS 7，默认是 Python 2.7。于是，你花费大量时间解决环境依赖冲突，这就是著名的“环境地狱”。

  **传统虚拟机（VM）的解决方案：** 虚拟机通过在宿主机操作系统上运行一个完整的“客户操作系统”（Guest OS），来提供隔离的环境。这就像在公寓楼里，每家每户（虚拟机）都拥有自己完整的一套基础设施（完整操作系统），包括地基、水电、墙壁。这非常重，启动一个虚拟机通常需要几分钟，占用数 GB 的磁盘空间。

  **Docker 容器的解决方案：** 容器则不同。它并非模拟一个完整的操作系统，而是与宿主机**共享操作系统内核**。容器只是一个被隔离的用户空间进程。它只包含应用本身及其运行时所需的依赖（库、二进制文件、配置文件等），但不包含内核。这就像一套公寓里的不同房间（容器），它们共享大楼的基础设施（宿主机内核），但每个房间有自己的家具和装修（应用和依赖）。

  **Docker 的三大核心组件：**

  1.  **镜像（Image）：** 镜像是一个轻量级、可执行的独立软件包，包含运行某个软件所需的所有内容：代码、运行时、系统工具、系统库和设置。你可以把镜像理解为面向对象的“类”，它是一个只读的模板。比如，`python:3.9-slim` 就是一个官方提供的、精简版的 Python 3.9 运行环境镜像。
  2.  **容器（Container）：** 容器是镜像的运行实例。你可以启动、停止、删除、暂停一个容器。容器是“活”的，它拥有自己的文件系统、网络栈和进程空间。你可以把容器理解为面向对象的“对象”，它是从“类”（镜像）实例化出来的。你可以从同一个镜像启动多个容器，它们彼此隔离。
  3.  **仓库（Repository）：** 仓库是集中存放镜像文件的地方。最著名的公共仓库是 **Docker Hub** (hub.docker.com)。你可以从仓库拉取（`pull`）别人制作好的镜像，也可以将自己制作的镜像推送（`push`）到仓库，实现共享。

  总结一下：**镜像**是静态的蓝图，**容器**是动态的运行实例，**仓库**是存放蓝图的图书馆。理解了这三个概念，你就掌握了 Docker 的精髓。

### 1.2 Docker 安装与 Hello World

- **学习目标：**
  - 能在自己的操作系统上成功安装 Docker Desktop。
  - 掌握 `docker --version` 命令验证安装。
  - 运行第一个 Docker 容器：`docker run hello-world`。

- **讲义：**

  理论讲完了，让我们来点实际的。Docker 的安装非常简便，官方提供了 Docker Desktop 工具，支持 Windows、macOS 和 Linux。强烈建议初学者使用 Docker Desktop，它包含了 Docker 引擎 (Docker Engine)、Docker CLI 客户端、Docker Compose 等一系列工具。

  **安装步骤（以 Windows/macOS 为例）：**
  1.  访问 Docker 官方网站 [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)。
  2.  下载对应您操作系统的安装包。
  3.  双击运行安装程序，按照提示完成安装（通常一路默认即可）。
  4.  安装完成后，Docker Desktop 会自动启动。您会在系统托盘或菜单栏看到 Docker 的鲸鱼图标。
  5.  打开终端（Windows 使用 PowerShell 或 CMD，macOS 使用 Terminal），输入以下命令验证安装：

      ```bash
      docker --version
      ```

      你应该会看到类似 `Docker version 24.0.7, build afdd53b` 的输出。

  **运行您的第一个容器：Hello World**

  Docker 的 Hello World 示例是一个经典的入门仪式。它不是一个简单的打印语句，而是一个完整的流程演示。

  ```bash
  docker run hello-world
  ```

  执行这条命令后，Docker 会做以下几件事：
  1.  **检查本地镜像缓存：** Docker 首先检查你的电脑上是否已经存在名为 `hello-world` 的镜像。
  2.  **从仓库拉取镜像：** 如果本地没有，Docker 会默认从 Docker Hub 官方仓库拉取（下载）这个镜像。
  3.  **创建并启动容器：** 镜像下载完成后，Docker 会基于这个镜像创建一个新的容器，并在其中运行默认命令。
  4.  **输出信息：** 容器运行后，会输出一大段说明文字，解释 Docker 刚刚做了什么，并确认你的 Docker 安装正确且能正常工作。

  看到那段信息输出后，你的 Docker 环境就搭建成功了！你可以用 `docker ps -a` 命令查看刚刚运行过的容器（它现在处于“已退出”状态）。

  ```bash
  docker ps -a
  ```

  恭喜你，你已经成功迈出了 Docker 之旅的第一步！

---

## 第二章 Docker 镜像与容器操作

### 2.1 管理 Docker 镜像

- **学习目标：**
  - 掌握 `docker pull` 拉取特定版本的镜像。
  - 掌握 `docker images` 列出本地镜像。
  - 掌握 `docker rmi` 删除本地镜像。
  - 理解镜像的标签（Tag）概念。

- **讲义：**

  镜像管理是日常使用 Docker 最频繁的操作之一。让我们深入学习如何操作镜像。

  **1. 拉取镜像：`docker pull`**
  从远程仓库（默认是 Docker Hub）下载镜像到本地。语法是 `docker pull [选项] 仓库名[:标签]`。

  ```bash
  # 拉取最新版的 Ubuntu 镜像（标签为 latest）
  docker pull ubuntu

  # 拉取指定版本的 Nginx 镜像（标签为 1.25）
  docker pull nginx:1.25

  # 拉取特定平台的镜像（例如，在 ARM Mac 上拉取 amd64 架构的镜像）
  docker pull --platform linux/amd64 ubuntu
  ```

  **2. 列出本地镜像：`docker images`**
  这个命令会显示你本机所有已下载的镜像列表。

  ```bash
  docker images
  ```

  输出通常包含仓库名（REPOSITORY）、标签（TAG）、镜像 ID（IMAGE ID）、创建时间（CREATED）和大小（SIZE）。注意，镜像 ID 是一个 64 位十六进制字符串的缩写。

  **3. 理解镜像标签（Tag）**
  标签用于标识同一个镜像的不同版本。例如，`ubuntu:18.04`、`ubuntu:20.04`、`ubuntu:22.04` 都是 Ubuntu 镜像，但内置的软件包版本不同。`latest` 是一个特殊的标签，通常指向最新的稳定版本。**建议在生产环境中始终指定明确的版本标签，而不是依赖 `latest`**，以确保环境的一致性。

  **4. 删除镜像：`docker rmi`**
  当不再需要某个镜像时，可以用此命令删除。语法是 `docker rmi [选项] 镜像名[:标签] 或 镜像ID`。

  ```bash
  # 通过镜像名和标签删除
  docker rmi nginx:1.25

  # 通过镜像 ID 删除
  docker rmi 1234567890ab

  # 强制删除（即使有容器正在使用该镜像）
  docker rmi -f ubuntu
  ```

  **注意：** 如果有一个正在运行或已停止的容器正在使用该镜像，Docker 会阻止你删除它。你需要先删除所有相关的容器（`docker rm`），或者使用 `-f` 强制删除（不推荐，可能导致孤儿容器）。

### 2.2 管理 Docker 容器

- **学习目标：**
  - 掌握 `docker run` 的常用参数（`-d`, `-it`, `--name`, `-p`, `-v`）。
  - 掌握 `docker ps` 查看容器状态。
  - 掌握 `docker start`, `docker stop`, `docker restart`, `docker rm` 等容器生命周期管理命令。
  - 掌握 `docker exec` 进入运行中的容器。

- **讲义：**

  容器是镜像的实例，是真正运行应用的地方。本课我们将学习如何驾驭容器。

  **1. 创建并启动容器：`docker run`**
  这是最核心的命令。它相当于 `docker create` + `docker start`。基本语法：`docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`

  **常用选项详解：**
  - `-d` 或 `--detach`：**后台运行**容器（守护态）。容器启动后，终端会回到宿主机的 shell 提示符，容器在后台默默运行。
  - `-it`：**交互式终端**。通常与 `-i`（保持标准输入打开）和 `-t`（分配一个伪终端）组合使用。这让你可以像 SSH 登录一样进入容器内部。例如：`docker run -it ubuntu bash` 会启动一个 Ubuntu 容器并直接进入其 bash shell。
  - `--name`：为容器**命名**。如果不指定，Docker 会随机生成一个名字（如 `stoic_mclean`）。使用有意义的名称便于管理。
  - `-p`：**端口映射**。格式是 `宿主机端口:容器端口`。例如，`-p 8080:80` 会将宿主机的 8080 端口映射到容器的 80 端口。这样，你访问 `http://localhost:8080` 就相当于访问了容器内的 Web 服务。
  - `-v` 或 `--volume`：**挂载卷**。将宿主机上的一个目录或文件挂载到容器内的一个目录。用于数据持久化和代码热更新。例如，`-v /my/local/path:/app/data`。

  **示例：运行一个 Nginx Web 服务器**
  ```bash
  # 以后台方式运行一个名为 my-nginx 的 Nginx 容器
  # 将宿主机 8080 端口映射到容器 80 端口
  docker run -d --name my-nginx -p 8080:80 nginx:latest
  ```
  运行后，打开浏览器访问 `http://localhost:8080`，你应该能看到 Nginx 的欢迎页面。

  **2. 查看容器列表：`docker ps`**
  - `docker ps`：仅显示**正在运行**的容器。
  - `docker ps -a`：显示**所有**容器（包括已停止的）。

  **3. 容器生命周期管理**
  - `docker stop [容器名/ID]`：正常停止容器（发送 SIGTERM 信号，等待进程优雅退出）。
  - `docker start [容器名/ID]`：启动一个已停止的容器。
  - `docker restart [容器名/ID]`：重启容器。
  - `docker rm [容器名/ID]`：删除一个已停止的容器。如果要强制删除正在运行的容器，加 `-f` 参数。

  **4. 进入运行中的容器：`docker exec`**
  有时候我们需要进入一个正在后台运行的容器内部进行调试或查看日志。`docker exec` 就是干这个的。

  ```bash
  # 进入 my-nginx 容器，并启动一个 bash shell
  # -it 参数在这里同样重要，用于交互
  docker exec -it my-nginx bash
  ```
  现在你就进入了容器内部。你可以查看 `/etc/nginx/` 下的配置文件，或者查看 `/var/log/nginx/` 下的日志。输入 `exit` 可以退出容器，**此时容器本身并不会停止**，它仍在后台运行。

  **总结一下常用命令组合：**
  ```bash
  # 1. 拉取镜像
  docker pull nginx:alpine

  # 2. 运行容器
  docker run -d --name web -p 8888:80 nginx:alpine

  # 3. 查看运行状态
  docker ps

  # 4. 进入容器
  docker exec -it web sh

  # 5. 在容器内查看文件 (在容器shell中)
  ls /usr/share/nginx/html

  # 6. 退出容器
  exit

  # 7. 停止并删除容器
  docker stop web
  docker rm web

  # 8. 查看所有容器确认删除
  docker ps -a
  ```

---

## 第三章 构建自定义镜像：Dockerfile 基础

### 3.1 初识 Dockerfile

- **学习目标：**
  - 理解 Dockerfile 的作用和基本语法。
  - 掌握 `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD` 等核心指令。
  - 能够编写一个简单的 Dockerfile 来容器化一个 Python/Node.js 应用。

- **讲义：**

  使用官方镜像（如 `nginx`、`ubuntu`）很方便，但大多数时候，我们需要构建包含自己应用代码的镜像。Dockerfile 就是一份构建镜像的“配方”或“脚本”。它是一个纯文本文件，包含了一系列指令，Docker 引擎会逐条执行这些指令，最终生成一个自定义镜像。

  **Dockerfile 核心指令详解：**

  1.  **`FROM`**：**基础镜像**。所有 Dockerfile 都必须以 `FROM` 开始。它指定了我们新镜像基于哪个现有镜像构建。一个好的基础镜像应该足够小，只包含运行你的应用所必需的东西。例如，`FROM python:3.9-slim` 或 `FROM node:18-alpine`。
  2.  **`WORKDIR`**：**工作目录**。设置后续指令（如 `RUN`、`CMD`、`COPY`、`ADD`）的执行目录。如果目录不存在，Docker 会自动创建。最佳实践是始终设置一个工作目录，避免使用根目录。
  3.  **`COPY`**：**复制文件**。将宿主机上的文件或目录复制到容器的文件系统中。格式是 `COPY <源路径> <目标路径>`。`<源路径>` 是相对于 Dockerfile 所在目录的路径。
  4.  **`RUN`**：**运行命令**。在构建镜像的过程中执行命令。通常用于安装软件包、创建用户、设置权限等。每一条 `RUN` 指令都会在当前的镜像层之上创建一个新的层。为了减小镜像体积，我们经常将多个 `RUN` 命令用 `&&` 连接起来。
  5.  **`CMD`**：**容器启动命令**。指定容器启动时要运行的命令。一个 Dockerfile 中只能有一条 `CMD` 指令。它的主要作用是提供容器的默认执行行为。如果 `docker run` 时指定了其他命令，`CMD` 会被覆盖。例如，`CMD ["python", "app.py"]`。

  **一个简单的 Python Flask 应用 Dockerfile 示例：**

  假设你的项目结构如下：
  ```
  my-flask-app/
  ├── app.py
  ├── requirements.txt
  └── Dockerfile
  ```

  - `app.py`:
    ```python
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello from Dockerized Flask App!"

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
    ```

  - `requirements.txt`:
    ```
    Flask==2.3.2
    ```

  - `Dockerfile`:
    ```dockerfile
    # 使用官方 Python 3.9 精简版作为基础镜像
    FROM python:3.9-slim

    # 设置容器内的工作目录为 /app
    WORKDIR /app

    # 将宿主机当前目录下的 requirements.txt 复制到容器的工作目录
    COPY requirements.txt .

    # 运行 pip 安装依赖
    RUN pip install --no-cache-dir -r requirements.txt

    # 将宿主机当前目录下的所有文件复制到容器的工作目录
    COPY . .

    # 声明容器运行时监听的端口（仅为文档说明，不真正映射端口）
    EXPOSE 5000

    # 容器启动时运行的命令
    CMD ["python", "app.py"]
    ```

  这个 Dockerfile 清晰地描述了构建镜像的每一步：从基础环境开始，设置工作空间，安装依赖，复制代码，最后定义启动命令。

### 3.2 使用 `docker build` 构建镜像

- **学习目标：**
  - 掌握 `docker build -t` 命令构建自定义镜像。
  - 理解构建上下文（Build Context）的概念。
  - 能够通过 `docker history` 查看镜像的分层结构。

- **讲义：**

  编写好 Dockerfile 后，下一步就是使用 `docker build` 命令