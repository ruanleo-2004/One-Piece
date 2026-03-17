// 初始化卡片悬停效果
function initHoverEffect() {
    const cards = document.querySelectorAll(".r-card");

    cards.forEach((card) => {
        // 动态创建 <div class="card-overlay"></div>
        let overlay = card.querySelector(".card-overlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.className = "card-overlay";
            card.appendChild(overlay); // 添加到 card 内
        }

        // 查找 href 并解析数字
        const link = card.querySelector("a");
        if (link) {
            // 为蒙版添加点击事件，使用SPA路由导航
            overlay.addEventListener("click", (e) => {
                e.preventDefault();
                // 如果SPA路由器可用，使用其导航方法
                if (window.spaApp && window.spaApp.router) {
                    window.spaApp.router.navigateTo(link.getAttribute('href'));
                } else {
                    // 回退到传统导航
                    window.location.href = link.href;
                }
            });
        }
    });
}
