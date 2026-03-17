// 原生JavaScript SPA路由系统
class SPARouter {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        
        // 初始化contentContainer，支持多种容器类名
        const mainContentSelectors = ['.container.p-5.pb-0', '.container.mt-5', '.container'];
        for (const selector of mainContentSelectors) {
            this.contentContainer = document.querySelector(selector);
            if (this.contentContainer) break;
        }
        
        // 如果没有找到容器，创建一个默认容器
        if (!this.contentContainer) {
            this.contentContainer = document.createElement('div');
            this.contentContainer.className = 'container p-5 pb-0';
            document.body.appendChild(this.contentContainer);
        }
        
        this.navLinks = document.querySelectorAll('.nav-link');
        this.isTransitioning = false;
        
        // 初始化路由
        this.init();
    }
    
    // 初始化方法
    init() {
        // 绑定导航链接点击事件
        this.bindNavLinks();
        
        // 绑定所有页面内链接点击事件
        this.bindAllLinks();
        
        // 监听浏览器历史事件
        window.addEventListener('popstate', (e) => {
            this.handleRouteChange(e.state);
        });
        
        // 处理初始路由
        this.handleRouteChange(null, window.location.pathname);
    }
    
    // 注册路由
    registerRoute(path, callback) {
        this.routes[path] = callback;
    }
    
    // 绑定导航链接事件
    bindNavLinks() {
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                
                // 忽略个人中心相关链接，使用普通HTML跳转
                const personalCenterPaths = ['/home', '/index/home/', '/user/center', '/user/profile', '/user/favorites', '/user/editPassword'];
                const isPersonalCenter = personalCenterPaths.some(path => href.startsWith(path) || href === path.replace(/\/$/, ''));
                
                if (isPersonalCenter) {
                    // 如果是个人中心链接，执行音乐淡出后允许原生跳转
                    if (window.spaApp && window.spaApp.audioManager) {
                        // 阻止默认跳转
                        e.preventDefault();
                        // 执行音乐淡出，完成后再跳转
                        window.spaApp.audioManager.fadeOutAudio(() => {
                            // 音乐淡出完成后执行跳转
                            window.location.href = href;
                        });
                    }
                    // 不阻止默认行为，使用原生跳转
                    return;
                }
                
                e.preventDefault();
                this.navigateTo(href);
            });
        });
    }
    
    // 绑定所有页面内链接事件
    bindAllLinks() {
        // 使用事件委托监听整个文档的点击事件
        document.addEventListener('click', (e) => {
            // 查找被点击的链接元素
            const link = e.target.closest('a');
            
            // 如果点击的不是链接，直接返回
            if (!link) return;
            
            // 获取链接地址
            const href = link.getAttribute('href');
            
            // 如果没有href属性，直接返回
            if (!href) return;
            
            // 忽略外部链接
            if (href.startsWith('http://') || href.startsWith('https://')) {
                // 检查是否是本站链接
                const currentHost = window.location.hostname;
                try {
                    const linkHost = new URL(href).hostname;
                    if (linkHost !== currentHost) {
                        return; // 外部链接，不拦截
                    }
                } catch (e) {
                    return; // 无效URL，不拦截
                }
            }
            
            // 忽略锚点链接
            if (href.startsWith('#')) return;
            
            // 忽略下载链接
            if (link.hasAttribute('download')) return;
            
            // 忽略JavaScript链接
            if (href.startsWith('javascript:')) return;
            
            // 忽略个人中心相关链接（使用普通HTML跳转）
            const personalCenterPaths = ['/home', '/index/home/', '/user/center', '/user/profile', '/user/favorites', '/user/editPassword'];
            const isPersonalCenter = personalCenterPaths.some(path => href.startsWith(path) || href === path.replace(/\/$/, ''));
            if (isPersonalCenter) return;
            
            // 忽略收藏链接，让它们使用自己的点击事件处理
            if (href.includes('/blog/post/favorite') || href.includes('/blog/post/unfavorite')) {
                return;
            }
            
            // 防止默认跳转
            e.preventDefault();
            
            // 使用SPA路由导航
            this.navigateTo(href);
        });
        
        // 监听表单提交事件，防止整页刷新
        document.addEventListener('submit', (e) => {
            // 查找被提交的表单
            const form = e.target.closest('form');
            if (!form) return;
            
            // 忽略评论表单、回复表单和删除评论表单（已经在item.html中单独处理）
            if (form.closest('.comment-form') || form.closest('[id^="reply-form-"]') || (form.action.includes('/comment/') && form.action.includes('/delete'))) {
                return;
            }
            
            // 获取表单属性
            const action = form.getAttribute('action');
            const method = form.getAttribute('method') || 'GET';
            
            // 检查是否是博客系统相关的表单
            // 拦截所有博客系统的表单提交，使用AJAX处理，避免音乐终止
            if (action && (
                // 评论相关操作 (删除评论表单已在第138行忽略，这里不再处理)
                action.includes('/reply_comment') || 
                action.includes('/add_comment') ||
                // 博客相关操作
                action.includes('/blog/') ||
                // 博客文章相关
                action.includes('/post/') ||
                // 博客系列相关
                action.includes('/series/') ||
                // 博客话题相关
                action.includes('/topic/') ||
                // 博客新闻相关
                action.includes('/news/') ||
                // 博客关于我们联系表单
                action.includes('/about/concat') ||
                // 后台管理相关操作
                action.includes('/home/')
            )) {
                e.preventDefault();
                
                // 收集表单数据
                const formData = new FormData(form);
                
                // 发送AJAX请求
                fetch(action, {
                    method: method,
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(html => {
                    // 解析返回的HTML，更新页面内容
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    
                    // 查找评论区域
                    const commentsContainer = document.querySelector('.comments-container');
                    const newCommentsContainer = tempDiv.querySelector('.comments-container');
                    if (commentsContainer && newCommentsContainer) {
                        commentsContainer.innerHTML = newCommentsContainer.innerHTML;
                    }
                    
                    // 查找可能更新的内容区域
                    const contentContainer = document.querySelector('.container.p-5.pb-0');
                    const newContentContainer = tempDiv.querySelector('.container.p-5.pb-0');
                    if (contentContainer && newContentContainer) {
                        contentContainer.innerHTML = newContentContainer.innerHTML;
                    }
                    
                    // 查找可能更新的列表区域
                    const listContainer = document.querySelector('.list-container');
                    const newListContainer = tempDiv.querySelector('.list-container');
                    if (listContainer && newListContainer) {
                        listContainer.innerHTML = newListContainer.innerHTML;
                    }
                    
                    // 只需要刷新AOS以应用新元素，不需要重新初始化所有特效
                    if (window.AOS) {
                        window.AOS.refreshHard();
                    }
                })
                .catch(error => {
                    console.error('Form submission error:', error);
                    alert('操作失败，请稍后重试');
                });
            }
        });
    }
    
    // 导航到指定路径
    navigateTo(path, forceReload = false) {
        if (this.isTransitioning) return;
        
        // 检查是否导航到个人中心相关页面，如果是则音乐淡出
        if (path.includes('/user/center') || path.includes('/user/profile') || path.includes('/user/favorites') || path.includes('/user/editPassword')) {
            // 使用全局的spaApp实例来访问音频管理器
            if (window.spaApp && window.spaApp.audioManager) {
                // 阻止默认跳转
                this.isTransitioning = true;
                // 执行音乐淡出，完成后再跳转
                window.spaApp.audioManager.fadeOutAudio(() => {
                    // 音乐淡出完成后执行跳转
                    this.isTransitioning = false;
                    window.location.href = path;
                });
                return;
            }
        }
        
        // 更新浏览器历史
        window.history.pushState({ path }, '', path);
        
        // 处理路由变化
        this.handleRouteChange({ path }, null, forceReload);
    }
    
    // 处理路由变化
    handleRouteChange(state, initialPath = null, forceReload = false) {
        const path = state?.path || initialPath || window.location.pathname + window.location.search;
        
        // 忽略个人中心相关页面的路由处理，使用普通HTML页面加载
        const personalCenterPaths = ['/home', '/index/home/', '/user/center', '/user/profile', '/user/favorites', '/user/editPassword'];
        const isPersonalCenter = personalCenterPaths.some(personalPath => path.startsWith(personalPath) || path === personalPath.replace(/\/$/, ''));
        if (isPersonalCenter) {
            // 如果是个人中心页面，不执行SPA路由逻辑
            return;
        }
        
        if ((this.currentRoute === path && !forceReload) || this.isTransitioning) return;
        
        this.isTransitioning = true;
        this.currentRoute = path;
        
        // 执行页面过渡动画
        this.performTransition(() => {
            // 调用对应路由的回调函数
            if (this.routes[path]) {
                this.routes[path]();
            } else {
                // 默认路由处理
                this.loadPageContent(path);
            }
            
            // 更新导航状态
            this.updateNavActiveState(path);
            
            this.isTransitioning = false;
        });
    }
    
    // 执行页面过渡动画
    performTransition(callback) {
        // 清除所有可能的提示框元素，包括收藏提示、关注提示等
        const allTips = document.querySelectorAll('.favorite-tip, .follow-tip, .alert, .alert-success, .alert-info, .alert-warning, .alert-danger');
        allTips.forEach(tip => tip.remove());
        
        // 直接清空内容，不显示加载文本
        this.contentContainer.innerHTML = '';
        
        // 获取所有需要淡出的元素：非导航栏header和bottom-header
        const navHeader = document.querySelector('.navbar');
        const currentHeaders = document.querySelectorAll('header');
        const bottomHeaders = document.querySelectorAll('.bottom-header');
        
        // 创建一个Promise来处理所有需要淡出的元素
        const fadeOutElements = () => {
            return new Promise((resolve) => {
                let elementsToFade = [];
                
                // 1. 处理所有非导航栏header
                currentHeaders.forEach(header => {
                    if (header !== navHeader) {
                        elementsToFade.push(header);
                        
                        // 确保header在淡出过程中保持100%宽度
                        header.style.width = '100% !important';
                        header.style.maxWidth = 'none !important';
                        header.style.position = 'relative !important';
                        header.style.boxSizing = 'border-box !important';
                        header.style.overflow = 'hidden !important';
                        
                        // 为header容器添加统一的淡出动画
                        header.style.transition = 'opacity 0.5s ease-in-out !important';
                        header.style.opacity = '0 !important';
                        
                        // 确保所有子元素（包括img）与容器同步淡出
                        const children = header.querySelectorAll('*');
                        children.forEach(child => {
                            // 为子元素添加与容器相同的淡出动画
                            child.style.transition = 'opacity 0.5s ease-in-out !important';
                            child.style.opacity = '0 !important';
                            // 保持子元素原有的布局属性，仅同步透明度动画
                            if (child.tagName === 'IMG') {
                                // 保持图片原有的object-fit属性
                                child.style.objectFit = child.style.objectFit || 'contain';
                            }
                        });
                    }
                });
                
                // 2. 处理所有bottom-header
                bottomHeaders.forEach(bottomHeader => {
                    elementsToFade.push(bottomHeader);
                    
                    // 为bottom-header添加与header相同的淡出动画
                    bottomHeader.style.width = '100% !important';
                    bottomHeader.style.maxWidth = 'none !important';
                    bottomHeader.style.position = 'relative !important';
                    bottomHeader.style.boxSizing = 'border-box !important';
                    bottomHeader.style.overflow = 'hidden !important';
                    
                    // 为bottom-header容器添加统一的淡出动画
                    bottomHeader.style.transition = 'opacity 0.5s ease-in-out !important';
                    bottomHeader.style.opacity = '0 !important';
                    
                    // 确保所有子元素与容器同步淡出
                    const children = bottomHeader.querySelectorAll('*');
                    children.forEach(child => {
                        // 为子元素添加与容器相同的淡出动画
                        child.style.transition = 'opacity 0.5s ease-in-out !important';
                        child.style.opacity = '0 !important';
                        // 保持子元素原有的布局属性
                        if (child.tagName === 'IMG') {
                            child.style.objectFit = child.style.objectFit || 'contain';
                        }
                    });
                });
                
                // 如果没有元素需要淡出，直接resolve
                if (elementsToFade.length === 0) {
                    resolve();
                    return;
                }
                
                // 监听最后一个元素的过渡结束事件
                const lastElement = elementsToFade[elementsToFade.length - 1];
                const transitionEndHandler = () => {
                    lastElement.removeEventListener('transitionend', transitionEndHandler);
                    resolve();
                };
                
                lastElement.addEventListener('transitionend', transitionEndHandler);
                
                // 设置一个超时时间，确保即使过渡事件不触发也能继续执行
                setTimeout(resolve, 500);
            });
        };
        
        // 执行所有元素的淡出动画
        fadeOutElements().then(() => {
            // 清理特效
            if (window.spaApp && window.spaApp.effectsManager) {
                window.spaApp.effectsManager.cleanup();
            }
            
            // 执行回调，加载新页面内容
            callback();
            
            // 页面内容加载完成后，重新初始化特效
            if (window.spaApp && window.spaApp.effectsManager) {
                window.spaApp.effectsManager.initEffects();
            }
        });
    }
    
    // 加载页面内容
    loadPageContent(path) {
        // 确保path包含查询参数
        const fullPath = path.includes('?') ? path : path + window.location.search;
        fetch(fullPath, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            // 提取页面内容
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // 提取并替换header内容
            const headerContent = tempDiv.querySelector('header');
            const navHeader = document.querySelector('.navbar');
            
            // 先移除所有非导航栏的header
            const currentHeaders = document.querySelectorAll('header');
            currentHeaders.forEach(header => {
                if (header !== navHeader) {
                    header.remove();
                }
            });
            
            // 如果新页面有header且不是导航栏，则添加到导航栏之后
            if (headerContent && headerContent.className !== 'navbar') {
                // 确保新header保持与原设计一致的宽度和样式
                const newHeader = headerContent.cloneNode(true);
                
                // 确保header宽度为100%
                newHeader.style.width = '100% !important';
                newHeader.style.maxWidth = 'none !important';
                newHeader.style.boxSizing = 'border-box !important';
                newHeader.style.overflow = 'hidden !important';
                newHeader.style.position = 'relative !important';
                newHeader.style.margin = '0 !important';
                newHeader.style.padding = '0 !important';
                
                // 添加淡入动画
                newHeader.style.opacity = '0 !important';
                newHeader.style.transition = 'opacity 0.5s ease-in-out !important';
                
                // 插入新header
                if (navHeader.nextSibling) {
                    navHeader.parentNode.insertBefore(newHeader, navHeader.nextSibling);
                } else {
                    navHeader.parentNode.appendChild(newHeader);
                }
                
                // 保留子元素的原有样式和动画效果，只添加淡入效果
                const children = newHeader.querySelectorAll('*');
                children.forEach(child => {
                    // 为子元素添加淡入效果
                    child.style.transition = 'opacity 0.5s ease-in-out !important';
                    child.style.opacity = '0 !important';
                });
                
                // 触发重排，确保动画生效
                void newHeader.offsetWidth;
                
                // 应用淡入效果到header和所有子元素
                newHeader.style.opacity = '1 !important';
                // 直接使用之前声明的children变量，避免重复声明
                children.forEach(child => {
                    child.style.opacity = '1 !important';
                });
            }
            
            // 提取并替换secondary_header内容
            const secondaryHeaderContent = tempDiv.querySelector('.secondary-header');
            const currentSecondaryHeader = document.querySelector('.secondary-header');
            if (secondaryHeaderContent) {
                if (currentSecondaryHeader) {
                    currentSecondaryHeader.outerHTML = secondaryHeaderContent.outerHTML;
                } else if (secondaryHeaderContent.innerHTML.trim()) {
                    // 如果当前没有secondary_header但新页面有，则添加到header之后
                    const header = document.querySelector('header:not(.navbar)');
                    if (header) {
                        header.insertAdjacentHTML('afterend', secondaryHeaderContent.outerHTML);
                    } else {
                        // 如果没有header，则添加到contentContainer之前
                        this.contentContainer.insertAdjacentHTML('beforebegin', secondaryHeaderContent.outerHTML);
                    }
                }
            } else if (currentSecondaryHeader) {
                // 如果新页面没有secondary_header但当前有，则移除
                currentSecondaryHeader.remove();
            }
            
            // 提取并替换main内容，支持多种容器类名
            const mainContentSelectors = ['.container.p-5.pb-0', '.container.mt-5', '.container'];
            let mainContent = null;
            
            // 尝试匹配多种容器类名
            for (const selector of mainContentSelectors) {
                mainContent = tempDiv.querySelector(selector);
                if (mainContent) break;
            }
            
            if (mainContent) {
                // 提取所有script标签
                const scripts = mainContent.querySelectorAll('script');
                // 移除script标签但保留其他内容
                const clonedMainContent = mainContent.cloneNode(true);
                clonedMainContent.querySelectorAll('script').forEach(script => script.remove());
                
                // 插入HTML内容（不包含script标签）
                this.contentContainer.innerHTML = clonedMainContent.innerHTML;
                // 页面内容加载完成后，滚动到顶部
                window.scrollTo(0, 0);
                
                // 执行所有提取的script标签
                scripts.forEach(script => {
                    const newScript = document.createElement('script');
                    // 复制script的属性
                    for (let attr of script.attributes) {
                        newScript.setAttribute(attr.name, attr.value);
                    }
                    // 复制script的内容
                    newScript.textContent = script.textContent;
                    // 执行script
                    document.body.appendChild(newScript);
                    // 执行后移除临时script标签
                    setTimeout(() => {
                        document.body.removeChild(newScript);
                    }, 0);
                });
            } else {
                this.contentContainer.innerHTML = '<div class="error">页面加载失败</div>';
                // 页面加载失败时也滚动到顶部
                window.scrollTo(0, 0);
            }
            
            // 提取并替换bottom_header内容
            const bottomHeaderContent = tempDiv.querySelector('.bottom-header');
            const currentBottomHeader = document.querySelector('.bottom-header');
            
            if (bottomHeaderContent && bottomHeaderContent.innerHTML.trim()) {
                // 创建新的bottom-header元素
                const newBottomHeader = document.createElement('div');
                newBottomHeader.className = bottomHeaderContent.className;
                newBottomHeader.innerHTML = bottomHeaderContent.innerHTML;
                
                // 应用初始样式
                newBottomHeader.style.width = '100% !important';
                newBottomHeader.style.maxWidth = 'none !important';
                newBottomHeader.style.position = 'relative !important';
                newBottomHeader.style.boxSizing = 'border-box !important';
                newBottomHeader.style.overflow = 'hidden !important';
                newBottomHeader.style.margin = '0 !important';
                newBottomHeader.style.padding = '0 !important';
                newBottomHeader.style.opacity = '0 !important';
                newBottomHeader.style.transition = 'opacity 0.5s ease-in-out !important';
                
                // 移除当前的bottom-header
                if (currentBottomHeader) {
                    currentBottomHeader.remove();
                }
                
                // 添加新的bottom-header
                this.contentContainer.insertAdjacentHTML('afterend', newBottomHeader.outerHTML);
                
                // 触发重排，确保动画生效
                const actualNewBottomHeader = document.querySelector('.bottom-header');
                if (actualNewBottomHeader) {
                    // 为bottom-header的子元素添加淡入效果
                    const children = actualNewBottomHeader.querySelectorAll('*');
                    children.forEach(child => {
                        child.style.transition = 'opacity 0.5s ease-in-out !important';
                        child.style.opacity = '0 !important';
                    });
                    
                    void actualNewBottomHeader.offsetWidth;
                    // 应用淡入效果到bottom-header和所有子元素
                    actualNewBottomHeader.style.opacity = '1 !important';
                    children.forEach(child => {
                        child.style.opacity = '1 !important';
                    });
                }
            } else if (currentBottomHeader) {
                // 如果新页面没有bottom_header但当前有，则移除
                currentBottomHeader.remove();
            }
            
            // 页面内容加载完成后重新初始化特效
            setTimeout(() => {
                // 检查是否是漫画页面，如果是则手动调用初始化函数
                if (window.location.pathname.includes('/gallery')) {
                    if (typeof initGalleryPage !== 'undefined') {
                        // 确保DOM元素加载完成后再调用
                        requestAnimationFrame(() => {
                            initGalleryPage();
                        });
                    } else {
                        console.error('initGalleryPage function not found');
                    }
                }
            }, 0);
        })
        .catch(error => {
            console.error('Error loading page:', error);
            this.contentContainer.innerHTML = '<div class="error">页面加载失败</div>';
        });
    }
    
    // 更新导航激活状态
    updateNavActiveState(path) {
        this.navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === path) {
                link.parentElement.classList.add('active');
            } else {
                link.parentElement.classList.remove('active');
            }
        });
    }
}

// 全局音频管理器
class AudioManager {
    constructor() {
        this.audioElement = null;
        this.isPlaying = false;
        this.audioToggle = null;
        this.audioIcon = null;
        this.isPreloaded = false;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        // 获取音频元素
        this.audioElement = document.getElementById('background-audio');
        this.audioToggle = document.getElementById('audio-toggle');
        this.audioIcon = document.getElementById('audio-icon');
        this.audioPlayerContainer = document.getElementById('audio-player-container');
        
        if (this.audioElement && this.audioToggle) {
            // 预加载音频
            this.preloadAudio();
            
            // 绑定播放控制事件
            this.audioToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePlay();
            });
            
            // 初始化拖拽功能
            this.initDrag();
            
            // 设置音频事件监听
            this.setupAudioEvents();
        }
    }
    
    // 预加载音频
    preloadAudio() {
        if (!this.audioElement || this.isLoading || this.isPreloaded) return;
        
        this.isLoading = true;
        
        // 设置音频为预加载模式
        this.audioElement.preload = 'auto';
        
        // 监听加载完成事件
        this.audioElement.addEventListener('canplaythrough', () => {
            this.isPreloaded = true;
            this.isLoading = false;
            console.log('音频预加载完成');
        }, { once: true });
        
        // 开始加载
        this.audioElement.load();
    }
    
    togglePlay() {
        if (!this.audioElement) return;
        
        if (this.isPlaying) {
            // 暂停音频
            this.audioElement.pause();
            this.isPlaying = false;
            this.updateUI();
        } else {
            // 播放音频
            if (this.isPreloaded) {
                // 如果音频已预加载，直接播放
                this.playAudio();
            } else if (!this.isLoading) {
                // 如果音频未加载，先加载再播放
                this.preloadAudio();
                // 监听加载完成后自动播放
                this.audioElement.addEventListener('canplaythrough', () => {
                    this.playAudio();
                }, { once: true });
            }
        }
    }
    
    // 实际播放音频的方法
    playAudio() {
        if (!this.audioElement) return;
        
        this.audioElement.play()
            .then(() => {
                this.isPlaying = true;
                this.updateUI();
            })
            .catch(error => {
                console.error('Audio play error:', error);
                // 处理自动播放限制
                this.handleAutoplayRestriction();
            });
    }
    
    setupAudioEvents() {
        this.audioElement.addEventListener('ended', () => {
            this.isPlaying = false;
            this.updateUI();
        });
        
        this.audioElement.addEventListener('play', () => {
            this.isPlaying = true;
            this.updateUI();
        });
        
        this.audioElement.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updateUI();
        });
    }
    
    updateUI() {
        if (this.audioToggle && this.audioIcon) {
            if (this.isPlaying) {
                this.audioToggle.classList.remove('paused');
                this.audioToggle.classList.add('playing');
                this.audioIcon.classList.remove('fa-pause');
                this.audioIcon.classList.add('fa-music');
            } else {
                this.audioToggle.classList.remove('playing');
                this.audioToggle.classList.add('paused');
                this.audioIcon.classList.remove('fa-music');
                this.audioIcon.classList.add('fa-pause');
            }
        }
    }
    
    handleAutoplayRestriction() {
        // 创建用户交互提示
        const message = '请点击页面任意位置开始播放音乐';
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            font-size: 24px;
            cursor: pointer;
        `;
        overlay.textContent = message;
        
        // 添加点击事件
        overlay.addEventListener('click', () => {
            this.audioElement.play()
                .then(() => {
                    this.isPlaying = true;
                    this.updateUI();
                    document.body.removeChild(overlay);
                })
                .catch(error => {
                    console.error('Audio play error after user interaction:', error);
                });
        });
        
        document.body.appendChild(overlay);
    }
    
    // 初始化拖拽功能
    initDrag() {
        if (!this.audioPlayerContainer) return;
        
        let isDragging = false;
        let offsetX, offsetY;
        
        // 鼠标按下事件
        this.audioPlayerContainer.addEventListener('mousedown', (e) => {
            // 如果点击的是播放按钮，不执行拖拽
            if (e.target === this.audioToggle || this.audioToggle.contains(e.target)) {
                return;
            }
            
            isDragging = true;
            offsetX = e.clientX - this.audioPlayerContainer.getBoundingClientRect().left;
            offsetY = e.clientY - this.audioPlayerContainer.getBoundingClientRect().top;
            
            // 更改鼠标样式
            document.body.style.cursor = 'move';
        });
        
        // 鼠标移动事件
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const x = e.clientX - offsetX;
            const y = e.clientY - offsetY;
            
            // 设置新位置
            this.audioPlayerContainer.style.left = `${x}px`;
            this.audioPlayerContainer.style.top = `${y}px`;
            this.audioPlayerContainer.style.bottom = 'auto';
            this.audioPlayerContainer.style.right = 'auto';
        });
        
        // 鼠标释放事件
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                document.body.style.cursor = 'auto';
            }
        });
        
        // 触摸事件支持
        this.audioPlayerContainer.addEventListener('touchstart', (e) => {
            if (e.target === this.audioToggle || this.audioToggle.contains(e.target)) {
                return;
            }
            
            isDragging = true;
            const touch = e.touches[0];
            offsetX = touch.clientX - this.audioPlayerContainer.getBoundingClientRect().left;
            offsetY = touch.clientY - this.audioPlayerContainer.getBoundingClientRect().top;
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            
            e.preventDefault();
            const touch = e.touches[0];
            const x = touch.clientX - offsetX;
            const y = touch.clientY - offsetY;
            
            this.audioPlayerContainer.style.left = `${x}px`;
            this.audioPlayerContainer.style.top = `${y}px`;
            this.audioPlayerContainer.style.bottom = 'auto';
            this.audioPlayerContainer.style.right = 'auto';
        });
        
        document.addEventListener('touchend', () => {
            isDragging = false;
        });
    }
    
    // 音频淡出方法
    fadeOutAudio(callback = null) {
        if (!this.audioElement || !this.isPlaying) {
            if (callback) callback();
            return;
        }
        
        // 开始淡出过程
        const fadeInterval = setInterval(() => {
            if (this.audioElement.volume > 0.15) {
                // 每次减少15%的音量
                this.audioElement.volume -= 0.15;
            } else {
                // 音量降到足够低后停止播放
                this.audioElement.pause();
                this.audioElement.volume = 1; // 重置音量为最大值
                this.isPlaying = false;
                this.updateUI();
                clearInterval(fadeInterval);
                
                // 执行回调函数
                if (callback) callback();
            }
        }, 150); // 每150毫秒调整一次音量（更慢的淡出速度，更长的淡出时间）
    }
}

// 资源缓存管理器
class ResourceCache {
    constructor() {
        this.cache = new Map();
        this.preloaded = new Set();
    }
    
    // 预加载单个资源
    preload(url) {
        if (this.preloaded.has(url)) return Promise.resolve(this.cache.get(url));
        
        return new Promise((resolve, reject) => {
            const ext = url.split('.').pop().toLowerCase();
            
            if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(ext)) {
                // 预加载图片
                const img = new Image();
                img.onload = () => {
                    this.cache.set(url, img);
                    this.preloaded.add(url);
                    resolve(img);
                };
                img.onerror = reject;
                img.src = url;
            } else if (['mp3', 'wav', 'ogg'].includes(ext)) {
                // 预加载音频
                const audio = new Audio();
                audio.oncanplaythrough = () => {
                    this.cache.set(url, audio);
                    this.preloaded.add(url);
                    resolve(audio);
                };
                audio.onerror = reject;
                audio.src = url;
            } else {
                // 预加载其他资源
                fetch(url)
                    .then(response => {
                        if (!response.ok) throw new Error('Resource not found');
                        return response.blob();
                    })
                    .then(blob => {
                        this.cache.set(url, blob);
                        this.preloaded.add(url);
                        resolve(blob);
                    })
                    .catch(reject);
            }
        });
    }
    
    // 批量预加载资源
    preloadAll(resources) {
        return Promise.all(resources.map(url => 
            this.preload(url).catch(error => {
                console.warn(`单个资源预加载失败: ${url}`, error);
                // 忽略单个资源加载失败，继续加载其他资源
                return null;
            })
        ));
    }
    
    // 获取缓存的资源
    get(url) {
        return this.cache.get(url);
    }
    
    // 检查资源是否已预加载
    isPreloaded(url) {
        return this.preloaded.has(url);
    }
}

// 页面特效管理器
class EffectsManager {
    constructor() {
        this.effects = [];
        this.webWorkers = [];
        this.resourceCache = new ResourceCache();
    }
    
    init() {
        // 预加载特效资源
        this.preloadEffects();
        
        // 只在页面初始加载时初始化特效，页面刷新时不重复初始化
        // 页面切换时的特效初始化由路由系统统一处理
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initEffects();
            });
        } else {
            // 检查是否是页面刷新导致的DOMContentLoaded已完成
            // 如果是SPA路由初始化，不重复执行特效
            if (!window.spaAppInitialized) {
                this.initEffects();
            }
        }
    }
    
    preloadEffects() {
        // 预加载图片资源（移除音频预加载，因为AudioManager已经负责音频的加载和播放）
        const images = [
            '/static/blog/images/路飞草帽.png',
            '/static/blog/images/face 1.jpg',
            '/static/blog/images/face 2.jpg',
            '/static/blog/images/face 3.jpg',
            '/static/blog/images/face 4.jpg',
            '/static/blog/images/face 5.jpg'
        ];
        
        // 批量预加载图片资源
        this.resourceCache.preloadAll(images)
            .then(() => {
                console.log('所有特效图片资源预加载完成');
            })
            .catch(error => {
                console.error('资源预加载失败:', error);
            });
    }
    
    initEffects() {
        // 初始化AOS动画
        if (window.AOS) {
            try {
                // 如果AOS未初始化，则初始化
                if (!window.AOS.isInitialized) {
                    window.AOS.init({
                        duration: 1200,
                        once: true
                    });
                    window.AOS.isInitialized = true;
                }
                
                // 检查是否是页面刷新场景（spaAppInitialized尚未设置但DOM已加载）
                if (!window.spaAppInitialized) {
                    // 对于页面刷新，手动触发header的AOS动画
                    const headerElements = document.querySelectorAll('header[data-aos="header-slide-left"]');
                    headerElements.forEach(header => {
                        // 确保header的初始状态是透明的
                        header.style.opacity = '0';
                        
                        // 手动添加AOS动画类来触发动画
                        header.classList.add('aos-init');
                        setTimeout(() => {
                            header.classList.add('aos-animate');
                        }, 10);
                    });
                } else {
                    // SPA应用内部页面切换时，刷新所有AOS动画
                    window.AOS.refreshHard();
                }
            } catch (error) {
                console.warn('AOS初始化/刷新失败:', error);
            }
        }
        
        // 初始化点击特效
        if (typeof initEffect !== 'undefined') {
            // 先移除旧的点击特效
            const clickEffectCanvas = document.getElementById('click-effect-canvas');
            if (clickEffectCanvas) {
                clickEffectCanvas.remove();
            }
            initEffect();
        }
        
        // 初始化星空背景
        if (typeof drawStars !== 'undefined') {
            // 先移除旧的星空背景
            const starCanvas = document.getElementById('canvas');
            if (starCanvas) {
                starCanvas.remove();
            }
            drawStars();
        }
        
        // 初始化卡片悬停效果
        if (typeof initHoverEffect !== 'undefined') {
            initHoverEffect();
        }
        
        // 初始化拖拽导航栏
        if (typeof initDragNav !== 'undefined') {
            initDragNav();
        }
    }
    
    // 创建Web Worker处理复杂计算
    createWorker(scriptUrl) {
        const worker = new Worker(scriptUrl);
        this.webWorkers.push(worker);
        
        // 设置Worker事件监听
        worker.addEventListener('message', (e) => {
            this.handleWorkerMessage(e);
        });
        
        return worker;
    }
    
    // 处理Worker消息
    handleWorkerMessage(e) {
        const { type, data } = e.data;
        
        switch (type) {
            case 'WORKER_READY':
                console.log('Effects Worker is ready');
                break;
            case 'STARS_CALCULATED':
                // 处理星星位置计算结果
                this.updateStarsPositions(data);
                break;
            default:
                console.warn('未知的Worker消息类型:', type);
        }
    }
    
    // 更新星星位置
    updateStarsPositions(positions) {
        // 这里可以将计算结果应用到Canvas渲染
        if (typeof updateStars !== 'undefined') {
            updateStars(positions);
        }
    }
    
    // 使用Worker计算星星位置
    calculateStarsWithWorker(stars, timePassed) {
        if (this.webWorkers.length > 0) {
            const worker = this.webWorkers[0];
            worker.postMessage({
                type: 'CALCULATE_STARS',
                data: { stars, timePassed }
            });
        }
    }
    
    // 销毁所有Web Worker
    destroyWorkers() {
        this.webWorkers.forEach(worker => {
            worker.terminate();
        });
        this.webWorkers = [];
    }
    
    // 完整清理特效资源
    cleanup() {
        // 终止所有Web Worker
        this.destroyWorkers();
        
        // 移除点击特效canvas
        const clickEffectCanvas = document.getElementById('click-effect-canvas');
        if (clickEffectCanvas) {
            clickEffectCanvas.remove();
        }
        
        // 清理星空背景（如果启用）
        const starCanvas = document.getElementById('canvas');
        if (starCanvas) {
            starCanvas.remove();
        }
        
        // 取消动画帧
        if (window.clickEffectAnimationId) {
            window.cancelAnimationFrame(window.clickEffectAnimationId);
            window.clickEffectAnimationId = null;
        }
        
        // 取消星空动画帧
        if (window.starAnimationId) {
            window.cancelAnimationFrame(window.starAnimationId);
            window.starAnimationId = null;
        }
        
        // 移除事件监听器
        if (window.clickEffectHandler) {
            document.removeEventListener('click', window.clickEffectHandler);
            window.clickEffectHandler = null;
        }
        
        // 重置AOS动画，但保留header的特效
        if (window.AOS) {
            // 移除所有AOS相关的类和属性，但保留header元素
            document.querySelectorAll('[data-aos]').forEach(el => {
                // 只处理非header元素
                if (el.tagName !== 'HEADER') {
                    // 移除所有AOS动画类
                    el.classList.remove('aos-init', 'aos-animate');
                    
                    // 移除AOS生成的样式和数据属性
                    el.removeAttribute('data-aos-id');
                    el.removeAttribute('style');
                } else {
                    // 对于header元素，只移除AOS生成的样式，保留AOS相关的类和data-aos属性
                    const currentStyle = el.getAttribute('style');
                    if (currentStyle) {
                        // 过滤掉AOS生成的动画样式，但保留opacity: 0和其他样式
                    const filteredStyles = currentStyle.split(';').filter(prop => 
                        !prop.includes('animation') && !prop.includes('transition') && 
                        !prop.includes('transform') || prop.includes('opacity: 0')
                    );
                    el.style.cssText = filteredStyles.join(';');
                    
                    // 确保header始终以透明状态开始动画
                    if (el.getAttribute('data-aos') === 'header-slide-left') {
                        el.style.opacity = '0';
                    }
                    }
                }
            });
            
            // 确保AOS初始化状态保持为true
            window.AOS.isInitialized = true;
        }
        
        // 清理悬停效果
        const cards = document.querySelectorAll('.r-card');
        cards.forEach(card => {
            const overlay = card.querySelector('.card-overlay');
            if (overlay) {
                overlay.remove();
            }
        });
        
        // 清理拖拽导航事件
        const draggableNav = document.getElementById('draggableNav');
        if (draggableNav) {
            if (window.dragMousedownHandler) {
                draggableNav.removeEventListener('mousedown', window.dragMousedownHandler);
                window.dragMousedownHandler = null;
            }
            if (window.dragMousemoveHandler) {
                document.removeEventListener('mousemove', window.dragMousemoveHandler);
                window.dragMousemoveHandler = null;
            }
            if (window.dragMouseupHandler) {
                document.removeEventListener('mouseup', window.dragMouseupHandler);
                window.dragMouseupHandler = null;
            }
        }
        
        // 清理可能的全局特效状态
        window.effects = null;
        window.currentEffect = null;
        
        // 清空特效数组
        this.effects = [];
    }
}

// SPA应用主类
class SPAApp {
    constructor() {
        this.router = null;
        this.audioManager = null;
        this.effectsManager = null;
        
        this.init();
    }
    
    init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupApp();
            });
        } else {
            this.setupApp();
        }
    }
    
    setupApp() {
        // 初始化音频管理器
        this.audioManager = new AudioManager();
        
        // 初始化特效管理器
        this.effectsManager = new EffectsManager();
        
        // 调用特效管理器的初始化方法
        this.effectsManager.init();
        
        // 创建Web Worker处理特效计算
        try {
            this.effectsManager.createWorker('/static/blog/js/effects-worker.js');
        } catch (error) {
            console.warn('Web Worker初始化失败:', error);
        }
        
        // 初始化路由
        this.router = new SPARouter();
        
        // 注册路由
        this.registerRoutes();
        
        // 为个人中心链接添加点击事件监听器，实现音乐淡出
        this.bindPersonalCenterLinks();
        
        // 设置应用已初始化标志，避免特效重复执行
        window.spaAppInitialized = true;
        console.log('SPA应用初始化完成');
    }
    
    // 绑定个人中心链接点击事件
    bindPersonalCenterLinks() {
        // 个人中心相关的路径
        const personalCenterPaths = [
            '/index/home/',
            '/user/center',
            '/user/profile',
            '/user/favorites',
            '/user/editPassword'
        ];
        
        // 为所有导航栏链接添加检查
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href) {
                // 检查是否是个人中心链接
                const isPersonalCenter = personalCenterPaths.some(path => {
                    // 检查href是否以个人中心路径开头或完全匹配
                    return href.startsWith(path) || href === path.replace(/\/$/, '');
                });
                
                if (isPersonalCenter) {
                    // 确保链接是普通HTML链接，不是SPA路由
                    link.addEventListener('click', (e) => {
                        // 阻止默认跳转
                        e.preventDefault();
                        // 触发音乐淡出，完成后再跳转
                        this.audioManager.fadeOutAudio(() => {
                            // 音乐淡出完成后执行跳转
                            window.location.href = href;
                        });
                        // 不阻止默认跳转，因为个人中心是普通HTML页面
                    });
                }
            }
        });
        
        // 为所有页面内的个人中心链接添加事件监听器
        const allLinks = document.querySelectorAll('a');
        allLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href) {
                // 检查是否是个人中心链接
                const isPersonalCenter = personalCenterPaths.some(path => {
                    return href.startsWith(path) || href === path.replace(/\/$/, '');
                });
                
                if (isPersonalCenter) {
                    // 确保链接是普通HTML链接，不是SPA路由
                    link.addEventListener('click', (e) => {
                        // 阻止默认跳转
                        e.preventDefault();
                        // 触发音乐淡出，完成后再跳转
                        this.audioManager.fadeOutAudio(() => {
                            // 音乐淡出完成后执行跳转
                            window.location.href = href;
                        });
                        // 不阻止默认跳转，因为个人中心是普通HTML页面
                    });
                }
            }
        });
    }
    
    registerRoutes() {
        // 注册所有导航页面路由（排除个人中心相关页面）
        const navPaths = [
            '/',
            '/blog/',
            '/blog/topic/',
            '/blog/news/',
            '/blog/gallery/',
            '/blog/post/',
            '/blog/about/concat/'
            // 移除个人中心路径，确保使用普通HTML链接跳转
        ];
        
        navPaths.forEach(path => {
            this.router.registerRoute(path, () => {
                this.router.loadPageContent(path);
            });
        });
    }
}

// 初始化SPA应用
document.addEventListener('DOMContentLoaded', () => {
    window.spaApp = new SPAApp();
    // 标记SPA应用初始化完成
    window.spaAppInitialized = true;
    
    // 直接初始化点击特效，确保草帽特效能正常工作
    if (typeof initEffect !== 'undefined') {
        // 先移除旧的点击特效
        const clickEffectCanvas = document.getElementById('click-effect-canvas');
        if (clickEffectCanvas) {
            clickEffectCanvas.remove();
        }
        initEffect();
        console.log('直接初始化点击特效');
    }
});