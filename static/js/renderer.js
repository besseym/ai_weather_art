class WeatherArtRenderer {
  constructor(containerId) {
    this.containerId = containerId;
    this.p5Instance = null;
    this.scene = null;
    this.particles = [];
  }

  render(sceneJSON) {
    this.scene = sceneJSON.scene;
    if (this.p5Instance) {
      this.p5Instance.remove();
    }
    this.particles = [];
    this.p5Instance = new p5((p) => {
      p.setup = () => this._setup(p);
      p.draw = () => this._draw(p);
    }, document.getElementById(this.containerId));
  }

  _setup(p) {
    const canvas = this.scene.canvas || { width: 800, height: 600 };
    p.createCanvas(canvas.width, canvas.height);
    this._initParticles(p);
  }

  _draw(p) {
    this._drawBackground(p);
    for (const element of this.scene.elements || []) {
      p.push();
      const opacity = element.opacity !== undefined ? element.opacity : 1.0;
      this._drawElement(p, element, opacity);
      p.pop();
    }
  }

  _drawBackground(p) {
    const bg = this.scene.background;
    if (!bg) {
      p.background(0);
      return;
    }
    if (bg.type === "solid") {
      p.background(bg.color);
    } else if (bg.type === "gradient") {
      this._drawGradient(p, bg);
    }
  }

  _drawGradient(p, bg) {
    const colors = bg.colors || ["#000000", "#000000"];
    const c1 = p.color(colors[0]);
    const c2 = p.color(colors[colors.length - 1]);

    p.noFill();
    if (bg.direction === "horizontal") {
      for (let x = 0; x <= p.width; x++) {
        const inter = p.map(x, 0, p.width, 0, 1);
        p.stroke(p.lerpColor(c1, c2, inter));
        p.line(x, 0, x, p.height);
      }
    } else {
      for (let y = 0; y <= p.height; y++) {
        const inter = p.map(y, 0, p.height, 0, 1);
        p.stroke(p.lerpColor(c1, c2, inter));
        p.line(0, y, p.width, y);
      }
    }
  }

  _drawElement(p, element, opacity) {
    switch (element.type) {
      case "ellipse":
        this._drawEllipse(p, element, opacity);
        break;
      case "rect":
        this._drawRect(p, element, opacity);
        break;
      case "line":
        this._drawLine(p, element, opacity);
        break;
      case "text":
        this._drawText(p, element, opacity);
        break;
      case "particle_system":
        this._updateAndDrawParticles(p, element, opacity);
        break;
      case "glow":
        this._drawGlow(p, element, opacity);
        break;
      default:
        console.warn(`Unknown element type: ${element.type}`);
    }
  }

  _applyFillStroke(p, element, opacity) {
    const alpha = Math.round(opacity * 255);
    if (element.fill) {
      const c = p.color(element.fill);
      c.setAlpha(alpha);
      p.fill(c);
    } else {
      p.noFill();
    }
    if (element.stroke) {
      const c = p.color(element.stroke);
      c.setAlpha(alpha);
      p.stroke(c);
      p.strokeWeight(element.stroke_weight || element.strokeWeight || 1);
    } else {
      p.noStroke();
    }
  }

  _drawEllipse(p, el, opacity) {
    this._applyFillStroke(p, el, opacity);
    p.ellipse(el.x, el.y, el.width, el.height);
  }

  _drawRect(p, el, opacity) {
    this._applyFillStroke(p, el, opacity);
    const cr = el.corner_radius || el.cornerRadius || 0;
    if (cr > 0) {
      p.rect(el.x, el.y, el.width, el.height, cr);
    } else {
      p.rect(el.x, el.y, el.width, el.height);
    }
  }

  _drawLine(p, el, opacity) {
    const alpha = Math.round(opacity * 255);
    const strokeColor = el.stroke || "#ffffff";
    const c = p.color(strokeColor);
    c.setAlpha(alpha);
    p.stroke(c);
    p.strokeWeight(el.stroke_weight || el.strokeWeight || 1);
    p.line(el.x1, el.y1, el.x2, el.y2);
  }

  _drawText(p, el, opacity) {
    const alpha = Math.round(opacity * 255);
    const c = p.color(el.fill || "#ffffff");
    c.setAlpha(alpha);
    p.fill(c);
    p.noStroke();
    p.textSize(el.size || 16);
    p.text(el.content, el.x, el.y);
  }

  _drawGlow(p, el, opacity) {
    const layers = 10;
    const baseColor = p.color(el.color || "#ffffff");
    const intensity = el.intensity || 0.5;
    p.noStroke();
    for (let i = layers; i >= 0; i--) {
      const r = p.map(i, 0, layers, 0, el.radius);
      const alpha = p.map(i, 0, layers, intensity * opacity * 255, 0);
      const c = p.color(p.red(baseColor), p.green(baseColor), p.blue(baseColor), alpha);
      p.fill(c);
      p.circle(el.x, el.y, r * 2);
    }
  }

  _initParticles(p) {
    this.particles = [];
    for (const element of this.scene.elements || []) {
      if (element.type === "particle_system") {
        const ps = [];
        const region = { x: 0, y: 0, width: p.width, height: p.height };
        const angleRad = p.radians(element.angle || 270);
        const speed = element.speed || 2;
        for (let i = 0; i < (element.count || 100); i++) {
          ps.push({
            x: region.x + p.random(region.width),
            y: region.y + p.random(region.height),
            vx: Math.cos(angleRad) * speed + (element.drift || 0) * p.random(-1, 1),
            vy: Math.sin(angleRad) * speed,
            size: element.size || 3,
          });
        }
        this.particles.push({ element, particles: ps, region });
      }
    }
  }

  _updateAndDrawParticles(p, element, opacity) {
    const group = this.particles.find((g) => g.element === element);
    if (!group) return;

    const alpha = Math.round(opacity * 255);
    const c = p.color(element.color || "#ffffff");
    c.setAlpha(alpha);
    const region = group.region;

    for (const pt of group.particles) {
      pt.x += pt.vx;
      pt.y += pt.vy;

      // Wrap around region edges
      if (pt.x < region.x) pt.x += region.width;
      if (pt.x > region.x + region.width) pt.x -= region.width;
      if (pt.y < region.y) pt.y += region.height;
      if (pt.y > region.y + region.height) pt.y -= region.height;

      p.noStroke();
      p.fill(c);

      const shape = element.particle_shape || element.particleShape || "circle";
      if (shape === "line") {
        const len = pt.size * 2;
        const angleRad = p.radians(element.angle || 270);
        p.stroke(c);
        p.strokeWeight(1);
        p.line(pt.x, pt.y, pt.x + Math.cos(angleRad) * len, pt.y + Math.sin(angleRad) * len);
      } else if (shape === "rect") {
        p.rect(pt.x, pt.y, pt.size, pt.size);
      } else {
        p.circle(pt.x, pt.y, pt.size);
      }
    }
  }

  destroy() {
    if (this.p5Instance) {
      this.p5Instance.remove();
      this.p5Instance = null;
    }
    this.particles = [];
    this.scene = null;
  }
}