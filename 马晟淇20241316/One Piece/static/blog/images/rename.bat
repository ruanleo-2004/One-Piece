@echo off
setlocal enabledelayedexpansion

:: 初始化计数器
set "count=1"

:: 遍历当前目录的所有文件
for %%f in (*.*) do (
    :: 获取文件的扩展名
    set "ext=%%~xf"
    :: 使用计数器重命名文件
    ren "%%f" "!count!!ext!"
    :: 计数器加1
    set /a count+=1
)

echo 所有文件已成功重命名！
pause
