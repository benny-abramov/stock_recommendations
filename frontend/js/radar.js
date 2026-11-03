/**
 * Custom 5-Axis Radar Chart Engine for Alpha Convergence Signals.
 * Visualizes:
 * 1. Technical Breakout
 * 2. Insider Conviction
 * 3. Analyst Alignment
 * 4. Value / Dip Reversal
 * 5. NLP Sentiment Buzz
 */

class ConvergenceRadar {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.labels = [
      'Technical Breakout',
      'Insider Conviction',
      'Analyst Alignment',
      'Dip Reversal (Value)',
      'Sentiment Buzz'
    ];
    this.scores = [50, 50, 50, 50, 50];
    this.colors = {
      polygonFill: 'rgba(0, 242, 254, 0.22)',
      polygonStroke: '#00f2fe',
      pointFill: '#ffffff',
      pointGlow: 'rgba(0, 242, 254, 0.6)',
      ring: 'rgba(255, 255, 255, 0.08)',
      spoke: 'rgba(255, 255, 255, 0.12)',
      label: '#94a3b8',
      scoreText: '#00f2fe'
    };

    window.addEventListener('resize', () => this.render());
  }

  setSignals(signalBreakdown) {
    if (!signalBreakdown) return;
    this.scores = [
      signalBreakdown.technical_score || 50,
      signalBreakdown.insider_score || 50,
      signalBreakdown.analyst_score || 50,
      signalBreakdown.drop_reversal_score || 50,
      signalBreakdown.sentiment_score || 50
    ];
    this.render();
  }

  resizeCanvas() {
    if (!this.canvas) return { width: 300, height: 260 };
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    return { width: rect.width, height: rect.height };
  }

  render() {
    if (!this.ctx || !this.canvas) return;
    const { width, height } = this.resizeCanvas();
    const ctx = this.ctx;
    ctx.clearRect(0, 0, width, height);

    const centerX = width / 2;
    const centerY = height / 2 + 6;
    const radius = Math.min(centerX, centerY) - 45;
    const numAxes = 5;
    const angleStep = (Math.PI * 2) / numAxes;
    const startAngle = -Math.PI / 2; // Start from top

    // 1. Draw Concentric Polygonal Background Rings (20%, 40%, 60%, 80%, 100%)
    const ringLevels = [0.2, 0.4, 0.6, 0.8, 1.0];
    ringLevels.forEach((level) => {
      ctx.beginPath();
      ctx.strokeStyle = this.colors.ring;
      ctx.lineWidth = 1;
      for (let i = 0; i < numAxes; i++) {
        const angle = startAngle + i * angleStep;
        const x = centerX + Math.cos(angle) * (radius * level);
        const y = centerY + Math.sin(angle) * (radius * level);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.stroke();
    });

    // 2. Draw Axis Spokes & Labels
    ctx.font = '10px "Inter", sans-serif';
    ctx.fillStyle = this.colors.label;

    for (let i = 0; i < numAxes; i++) {
      const angle = startAngle + i * angleStep;
      const xEnd = centerX + Math.cos(angle) * radius;
      const yEnd = centerY + Math.sin(angle) * radius;

      // Spoke
      ctx.beginPath();
      ctx.strokeStyle = this.colors.spoke;
      ctx.lineWidth = 1;
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(xEnd, yEnd);
      ctx.stroke();

      // Axis Label & Score
      const labelDistance = radius + 22;
      const lx = centerX + Math.cos(angle) * labelDistance;
      const ly = centerY + Math.sin(angle) * labelDistance;
      const text = this.labels[i];
      const score = Math.round(this.scores[i]);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = this.colors.label;
      ctx.fillText(text, lx, ly - 6);

      // Score pill
      ctx.fillStyle = this.colors.scoreText;
      ctx.font = 'bold 10px "JetBrains Mono", monospace';
      ctx.fillText(`${score}`, lx, ly + 7);
      ctx.font = '10px "Inter", sans-serif';
    }

    // 3. Draw Data Polygon
    ctx.beginPath();
    ctx.fillStyle = this.colors.polygonFill;
    ctx.strokeStyle = this.colors.polygonStroke;
    ctx.lineWidth = 2;

    const points = [];
    for (let i = 0; i < numAxes; i++) {
      const angle = startAngle + i * angleStep;
      const valRatio = Math.max(0.1, Math.min(1.0, this.scores[i] / 100));
      const px = centerX + Math.cos(angle) * (radius * valRatio);
      const py = centerY + Math.sin(angle) * (radius * valRatio);
      points.push({ x: px, y: py });
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // 4. Draw Glowing Data Points
    points.forEach((pt) => {
      ctx.save();
      ctx.shadowColor = this.colors.pointGlow;
      ctx.shadowBlur = 10;
      ctx.fillStyle = this.colors.pointFill;
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    });
  }
}

window.ConvergenceRadar = ConvergenceRadar;
