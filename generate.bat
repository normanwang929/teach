@echo off
chcp 65001 > nul
echo ================================================
echo   Teach Platform - 本地课程生成器
echo ================================================
echo.

if "%1"=="" (
    echo 用法：generate.bat "课程主题"
    echo.
    echo 示例：
    echo   generate.bat "Python 编程入门"
    echo   generate.bat "机器学习基础"
    echo.
    pause
    exit /b 1
)

set TOPIC=%1
set SLUG=%TOPIC: =_%

echo 🔍 第 1 步：搜索学习资料...
python scripts/search_course_materials.py "%TOPIC%" > teach-web/data/materials-%SLUG%.json 2>&1
echo ✅ 资料已保存到 teach-web/data/materials-%SLUG%.json
echo.

echo 📝 第 2 步：生成课程讲义...
python scripts/generate_course.py "%TOPIC%" ^
    --materials teach-web/data/materials-%SLUG%.json ^
    --output teach-web/lessons/%SLUG%
echo.

echo 🎙️  第 3 步：生成播客音频...
python scripts/podcast_generator.py ^
    --input teach-web/lessons/%SLUG%/course.md ^
    --output teach-web/lessons/%SLUG%/audio.mp3
echo.

echo 🎬 第 4 步：生成教学视频...
python scripts/video_generator.py ^
    --input teach-web/lessons/%SLUG%/course.md ^
    --audio teach-web/lessons/%SLUG%/audio.mp3 ^
    --output teach-web/lessons/%SLUG%/video.mp4
echo.

echo 📊 第 5 步：更新课程索引...
python scripts/update_course_index.py
echo.

echo ================================================
echo ✅ 课程生成完成！
echo.
echo 📂 课程目录：teach-web/lessons/%SLUG%/
echo 🌐 打开 teach-web/index.html 查看
echo ================================================
echo.
pause
