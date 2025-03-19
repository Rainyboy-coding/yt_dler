// GradientButton组件
class GradientButton extends HTMLElement {
  constructor() {
    super();
    this._variant = this.getAttribute("variant") || "default";
  }

  connectedCallback() {
    // 应用基础样式
    this.classList.add("gradient-button");

    // 应用变体样式
    if (this._variant === "variant") {
      this.classList.add("gradient-button-variant");
    }

    // 添加其他必要的样式类
    this.classList.add(
      "inline-flex",
      "items-center",
      "justify-center",
      "rounded-[11px]",
      "min-w-[132px]",
      "px-9",
      "py-4",
      "text-base",
      "leading-[19px]",
      "font-[500]",
      "text-white",
      "font-sans",
      "font-bold",
      "focus-visible:outline-none",
      "focus-visible:ring-1",
      "focus-visible:ring-ring",
      "disabled:pointer-events-none",
      "disabled:opacity-50"
    );

    // 为按钮添加额外样式（如果需要的话）
    this.style.cssText = `
      position: relative;
      cursor: pointer;
      background: radial-gradient(
        var(--spread-x) var(--spread-y) at var(--pos-x) var(--pos-y),
        var(--color-1) var(--stop-1),
        var(--color-2) var(--stop-2),
        var(--color-3) var(--stop-3),
        var(--color-4) var(--stop-4),
        var(--color-5) var(--stop-5)
      );
      transition:
        --pos-x 0.5s,
        --pos-y 0.5s,
        --spread-x 0.5s,
        --spread-y 0.5s,
        --color-1 0.5s,
        --color-2 0.5s,
        --color-3 0.5s,
        --color-4 0.5s,
        --color-5 0.5s,
        --border-angle 0.5s,
        --border-color-1 0.5s,
        --border-color-2 0.5s,
        --stop-1 0.5s,
        --stop-2 0.5s,
        --stop-3 0.5s,
        --stop-4 0.5s,
        --stop-5 0.5s;
    `;

    // 添加特效边框
    this.innerHTML = `
      <span class="border-effect"></span>
      <span class="button-content">${this.innerHTML}</span>
    `;

    // 为边框添加样式
    const borderEffect = this.querySelector(".border-effect");
    if (borderEffect) {
      borderEffect.style.cssText = `
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(
          var(--border-angle),
          var(--border-color-1),
          var(--border-color-2)
        );
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        pointer-events: none;
        z-index: 0;
      `;
    }

    // 为内容添加样式
    const buttonContent = this.querySelector(".button-content");
    if (buttonContent) {
      buttonContent.style.cssText = `
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
      `;
    }

    // 添加悬停效果
    this.addEventListener("mouseover", this._onMouseOver.bind(this));
    this.addEventListener("mouseout", this._onMouseOut.bind(this));
    this.addEventListener("click", this._onClick.bind(this));
  }

  // 鼠标悬停
  _onMouseOver() {
    if (this._variant !== "variant") {
      this.style.setProperty("--pos-x", "0%");
      this.style.setProperty("--pos-y", "91.51%");
      this.style.setProperty("--spread-x", "120.24%");
      this.style.setProperty("--spread-y", "103.18%");
      this.style.setProperty("--color-1", "#c96287");
      this.style.setProperty("--color-2", "#c66c64");
      this.style.setProperty("--color-3", "#cc7d23");
      this.style.setProperty("--color-4", "#37140a");
      this.style.setProperty("--color-5", "#000");
      this.style.setProperty("--border-angle", "190deg");
      this.style.setProperty("--border-color-1", "hsla(340, 78%, 90%, 0.1)");
      this.style.setProperty("--border-color-2", "hsla(340, 75%, 90%, 0.6)");
      this.style.setProperty("--stop-1", "0%");
      this.style.setProperty("--stop-2", "8.8%");
      this.style.setProperty("--stop-3", "21.44%");
      this.style.setProperty("--stop-4", "71.34%");
      this.style.setProperty("--stop-5", "85.76%");
    }
  }

  // 鼠标移出
  _onMouseOut() {
    if (this._variant !== "variant") {
      // 恢复默认值
      this.style.removeProperty("--pos-x");
      this.style.removeProperty("--pos-y");
      this.style.removeProperty("--spread-x");
      this.style.removeProperty("--spread-y");
      this.style.removeProperty("--color-1");
      this.style.removeProperty("--color-2");
      this.style.removeProperty("--color-3");
      this.style.removeProperty("--color-4");
      this.style.removeProperty("--color-5");
      this.style.removeProperty("--border-angle");
      this.style.removeProperty("--border-color-1");
      this.style.removeProperty("--border-color-2");
      this.style.removeProperty("--stop-1");
      this.style.removeProperty("--stop-2");
      this.style.removeProperty("--stop-3");
      this.style.removeProperty("--stop-4");
      this.style.removeProperty("--stop-5");
    }
  }

  // 点击效果
  _onClick() {
    this.style.transform = "scale(0.98)";
    setTimeout(() => {
      this.style.transform = "";
    }, 200);
  }

  // 处理变体属性变化
  static get observedAttributes() {
    return ["variant"];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (name === "variant") {
      if (oldValue === "variant") {
        this.classList.remove("gradient-button-variant");
      }
      if (newValue === "variant") {
        this.classList.add("gradient-button-variant");
      }
      this._variant = newValue;
    }
  }
}

// 注册组件
customElements.define("gradient-button", GradientButton);
