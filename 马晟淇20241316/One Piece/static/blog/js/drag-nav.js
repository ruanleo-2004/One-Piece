// 初始化拖拽导航栏
function initDragNav() {
    const draggableNav = document.getElementById('draggableNav');
    
    // 只有当元素存在时才执行拖拽功能
    if (draggableNav) {
        let isDragging = false; // 标记是否正在拖拽
        let offsetX, offsetY;

        // 鼠标按下事件 - 存储到全局变量以便清理
        window.dragMousedownHandler = (event) => {
            event.preventDefault(); // 阻止默认选中行为
            isDragging = true;
            draggableNav.classList.add('dragging');

            // 计算鼠标点击点与导航栏左上角的偏移
            offsetX = event.clientX - draggableNav.offsetLeft;
            offsetY = event.clientY - draggableNav.offsetTop;
        };
        draggableNav.addEventListener('mousedown', window.dragMousedownHandler);

        // 鼠标移动事件 - 存储到全局变量以便清理
        window.dragMousemoveHandler = (event) => {
            if (isDragging) {
                event.preventDefault(); // 阻止默认行为（如选中文本）

                // 限制导航栏在页面可视区域内
                const left = Math.min(
                    Math.max(event.clientX - offsetX, 0),
                    window.innerWidth - draggableNav.offsetWidth
                );
                const top = Math.min(
                    Math.max(event.clientY - offsetY, 0),
                    window.innerHeight - draggableNav.offsetHeight
                );

                draggableNav.style.left = `${left}px`;
                draggableNav.style.top = `${top}px`;
                draggableNav.style.right = 'auto'; // 解除右侧固定
            }
        };
        document.addEventListener('mousemove', window.dragMousemoveHandler);

        // 鼠标释放事件 - 存储到全局变量以便清理
        window.dragMouseupHandler = () => {
            isDragging = false;
            draggableNav.classList.remove('dragging');
        };
        document.addEventListener('mouseup', window.dragMouseupHandler);
    }
}

