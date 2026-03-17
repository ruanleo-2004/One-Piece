// JavaScript Document
document.addEventListener("DOMContentLoaded", () => {
  const galleryContainer = document.getElementById("gallery");

  // 生成图片路径
  for (let i = 1; i <= 56; i++) {
    const col = document.createElement("div");
    col.classList.add("col-6", "col-md-4", "col-lg-3");

    const img = document.createElement("img");
    img.src = `../images/gallery/${i}.png`;
    img.alt = `Image ${i}`;
    img.classList.add("img-fluid");

    col.appendChild(img);
    galleryContainer.appendChild(col);
  }

  // GSAP animations
  gsap.from("#gallery div", {
    opacity: 0,
    y: 50,
    duration: 0.6,
    stagger: 0.1,
    ease: "power1.out",
  });

  // Add hover animation using GSAP
  const images = document.querySelectorAll("#gallery img");
  images.forEach((img) => {
    img.addEventListener("mouseenter", () => {
      gsap.to(img, { scale: 1.2, duration: 0.3, ease: "power2.inOut" });
    });

    img.addEventListener("mouseleave", () => {
      gsap.to(img, { scale: 1, duration: 0.3, ease: "power2.inOut" });
    });
  });
});
