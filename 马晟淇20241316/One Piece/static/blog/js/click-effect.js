// JavaScript Document
// 简单版路飞草帽点击特效
// 移除自动执行，由effectsManager统一管理

// 暴露给全局的变量，用于清理
window.clickEffectAnimationId = null;
window.clickEffectHandler = null;
window.clickEffectCanvas = null;

function initEffect() {
    // 先移除可能存在的旧特效
    cleanupEffect();
    
    // 创建canvas元素
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // 设置canvas样式和ID
    canvas.id = 'click-effect-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '9999'; // 提高z-index确保能看到
    
    // 添加到页面
    document.body.appendChild(canvas);
    window.clickEffectCanvas = canvas;
    console.log('Canvas已添加到页面，当前位置:', canvas.offsetTop, canvas.offsetLeft);
    console.log('Canvas显示样式:', getComputedStyle(canvas).display);
    console.log('Canvas可见性:', getComputedStyle(canvas).visibility);
    console.log('Canvas z-index:', getComputedStyle(canvas).zIndex);
    console.log('Canvas位置:', getComputedStyle(canvas).position);
    
    // 调整canvas大小
    function resizeCanvas() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // 当前显示的草帽对象
    let currentHat = null;
    
    // 图片宽高比
    let imageAspectRatio = 1;
    
    // 加载草帽图片
    const hatImg = new Image();
    hatImg.src = '/static/blog/images/路飞草帽.png';
    let isImgLoaded = false;
    
    hatImg.onload = function() {
      isImgLoaded = true;
      // 计算原始图片宽高比
      imageAspectRatio = hatImg.width / hatImg.height;
    };
    
    hatImg.onerror = function(e) {
      console.error('草帽图片加载失败:', e);
    };
    
    // 创建草帽特效函数
    function createHatEffect(x, y) {
      // 创建一个新的草帽（size代表高度）
      currentHat = {
        x: x,
        y: y,
        size: 100, // 草帽高度
        alpha: 1,
        life: 1,
        delay: 0.15 // 延迟消失时间（单位：秒）
      };
    }
    
    // 渲染函数
    function render() {
      // 清空画布
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // 如果有草帽要显示
      if (currentHat && isImgLoaded) {
        console.log('渲染草帽 - 位置:', currentHat.x, currentHat.y, '透明度:', currentHat.alpha);
        // 保存画布状态
        ctx.save();
        
        // 设置透明度
        ctx.globalAlpha = currentHat.alpha;
        
        // 计算保持比例的宽度和高度
        const height = currentHat.size;
        const width = height * imageAspectRatio;
        
        // 绘制草帽图片（保持原始比例）
        ctx.drawImage(hatImg, currentHat.x - width / 2, currentHat.y - height / 2, width, height);
        
        // 恢复画布状态
        ctx.restore();
        
        // 更新草帽状态
        if (currentHat.delay > 0) {
          // 延迟期间，只减少延迟时间，不减少生命值
          currentHat.delay -= 0.025;
        } else {
          // 延迟结束，开始减少生命值（淡出）
          currentHat.life -= 0.025;
          currentHat.alpha = currentHat.life;
        }
        
        // 如果草帽生命周期结束，清除它
        if (currentHat.life <= 0) {
          currentHat = null;
        }
      }
      
      // 继续渲染并保存动画ID
      window.clickEffectAnimationId = requestAnimationFrame(render);
    }
    
    // 鼠标点击事件处理函数
    window.clickEffectHandler = function(e) {
      // 使用事件委托，确保SPA路由切换后仍然有效
      console.log('点击事件处理函数被调用:', e.clientX, e.clientY);
      createHatEffect(e.clientX, e.clientY);
    };
    
    // 使用事件委托，将事件绑定到document上，确保SPA路由切换后仍然有效
    document.addEventListener('click', window.clickEffectHandler, true); // 使用捕获阶段确保事件能被触发
    
    // 开始渲染
    render();
  }
  
  // 清理特效函数
  function cleanupEffect() {
    // 移除canvas
    if (window.clickEffectCanvas) {
      try {
        window.clickEffectCanvas.remove();
      } catch (e) {
        console.error('移除旧Canvas失败:', e);
      }
      window.clickEffectCanvas = null;
    }
    
    // 移除事件监听器
    if (window.clickEffectHandler) {
      try {
        document.removeEventListener('click', window.clickEffectHandler, true);
      } catch (e) {
        console.error('移除旧点击事件监听器失败:', e);
      }
      window.clickEffectHandler = null;
    }
    
    // 取消动画帧
    if (window.clickEffectAnimationId) {
      try {
        window.cancelAnimationFrame(window.clickEffectAnimationId);
      } catch (e) {
        console.error('取消旧动画帧失败:', e);
      }
      window.clickEffectAnimationId = null;
    }
  }
  
  // 确保在window上暴露cleanupEffect函数
  window.cleanupEffect = cleanupEffect;