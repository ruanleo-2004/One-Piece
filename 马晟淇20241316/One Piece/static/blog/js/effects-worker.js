// 特效处理Web Worker

// 星星计算函数
function calculateStarPosition(star, timePassed) {
    const x = Math.sin(timePassed) * star.orbitRadius + star.orbitX;
    const y = Math.cos(timePassed) * star.orbitRadius + star.orbitY;
    
    // 随机闪烁效果
    let alpha = star.alpha;
    const twinkle = Math.floor(Math.random() * 10);
    
    if (twinkle === 1 && alpha > 0) {
        alpha -= 0.05;
    } else if (twinkle === 2 && alpha < 1) {
        alpha += 0.05;
    }
    
    return {
        x,
        y,
        alpha,
        radius: star.radius
    };
}

// 处理消息
self.addEventListener('message', (e) => {
    const { type, data } = e.data;
    
    switch (type) {
        case 'CALCULATE_STARS':
            // 计算星星位置
            const { stars, timePassed } = data;
            const positions = stars.map(star => 
                calculateStarPosition(star, timePassed)
            );
            
            // 返回计算结果
            self.postMessage({
                type: 'STARS_CALCULATED',
                data: positions
            });
            break;
            
        case 'CALCULATE_EFFECT':
            // 处理其他特效计算
            // ...
            break;
            
        default:
            console.warn('未知的Worker消息类型:', type);
    }
});

// 向主线程发送就绪信号
self.postMessage({
    type: 'WORKER_READY'
});