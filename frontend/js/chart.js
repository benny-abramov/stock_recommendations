/**
 * Interactive Technical Charting Engine
 * Supports:
 * - Resolutions: 1D, 5D, 1M, 6M, 1Y, YTD
 * - Main Candlestick Chart + Volume Histogram
 * - Overlays: SMA20, SMA50, SMA200, EMA20, Bollinger Bands (20, 2)
 * - Sub-charts: RSI (14), MACD (12, 26, 9), OBV
 * - Interactive Crosshair HUD
 */

class TechnicalChart {
  constructor(mainCanvasId, subCanvasId, hudElementId) {
    this.mainCanvas = document.getElementById(mainCanvasId);
    this.subCanvas = document.getElementById(subCanvasId);
    this.hud = document.getElementById(hudElementId);
    
    this.mainCtx = this.mainCanvas ? this.mainCanvas.getContext('2d') : null;
    this.subCtx = this.subCanvas ? this.subCanvas.getContext('2d') : null;

    this.data = null;
    this.subIndicator = 'none'; // 'none' | 'rsi' | 'macd' | 'obv'
    if (this.subCanvas) {
      this.subCanvas.style.display = 'none';
    }
    this.hoverIndex = -1;

    this.priceMode = 'close'; // 'candles' (OHLC) | 'close' (Close line only)

    this.overlays = {
      sma20: false,
      sma50: false,
      sma200: false,
      ema20: false,
      bollinger: false
    };

    this.colors = {
      bullish: '#00e676',
      bearish: '#ff3366',
      volumeBullish: 'rgba(0, 230, 118, 0.25)',
      volumeBearish: 'rgba(255, 51, 102, 0.25)',
      sma20: '#00f2fe',
      sma50: '#ffb703',
      sma200: '#c77dff',
      ema20: '#4facfe',
      bbUpper: 'rgba(79, 172, 254, 0.7)',
      bbLower: 'rgba(79, 172, 254, 0.7)',
      bbFill: 'rgba(79, 172, 254, 0.08)',
      rsi: '#f72585',
      macd: '#00e676',
      macdSignal: '#ffb703',
      obv: '#48cae4',
      grid: 'rgba(255, 255, 255, 0.05)',
      text: '#94a3b8'
    };

    this.initEvents();
  }

  setPriceMode(mode) {
    this.priceMode = mode;
    this.render();
    if (this.data && this.data.candles && this.data.candles.length > 0) {
      const idx = this.hoverIndex >= 0 ? this.hoverIndex : this.data.candles.length - 1;
      this.updateHud(idx);
    }
  }

  setSubIndicator(name) {
    this.subIndicator = name;
    if (this.subCanvas) {
      this.subCanvas.style.display = (name === 'none') ? 'none' : 'block';
    }
    this.render();
  }

  toggleOverlay(name, state) {
    this.overlays[name] = state !== undefined ? state : !this.overlays[name];
    this.render();
  }

  setData(chartData) {
    this.data = chartData;
    this.hoverIndex = -1;
    this.render();
  }

  initEvents() {
    if (!this.mainCanvas) return;

    const handleMouseMove = (e) => {
      if (!this.data || !this.data.candles || this.data.candles.length === 0) return;
      const rect = this.mainCanvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const candleCount = this.data.candles.length;
      const plotWidth = rect.width - 65; // margin right
      const candleStep = plotWidth / candleCount;
      const idx = Math.floor(x / candleStep);
      
      if (idx >= 0 && idx < candleCount) {
        this.hoverIndex = idx;
        this.render();
        this.updateHud(idx);
      }
    };

    const handleMouseLeave = () => {
      this.hoverIndex = -1;
      this.render();
      if (this.data && this.data.candles.length > 0) {
        this.updateHud(this.data.candles.length - 1);
      }
    };

    this.mainCanvas.addEventListener('mousemove', handleMouseMove);
    this.mainCanvas.addEventListener('mouseleave', handleMouseLeave);
    
    if (this.subCanvas) {
      this.subCanvas.addEventListener('mousemove', handleMouseMove);
      this.subCanvas.addEventListener('mouseleave', handleMouseLeave);
    }

    window.addEventListener('resize', () => this.render());
  }

  updateHud(index) {
    if (!this.hud || !this.data || !this.data.candles || !this.data.candles[index]) return;
    const c = this.data.candles[index];
    const change = (c.close - c.open).toFixed(2);
    const changePct = (((c.close - c.open) / c.open) * 100).toFixed(2);
    const colorClass = c.close >= c.open ? 'color: var(--accent-green);' : 'color: var(--accent-red);';

    let extraIndicators = '';
    if (this.overlays.sma20 && this.data.sma20[index]) {
      extraIndicators += `<div class="hud-item"><span style="color:var(--color-sma20);">SMA20:</span><b class="hud-val">${this.data.sma20[index].value}</b></div>`;
    }
    if (this.overlays.sma50 && this.data.sma50[index]) {
      extraIndicators += `<div class="hud-item"><span style="color:var(--color-sma50);">SMA50:</span><b class="hud-val">${this.data.sma50[index].value}</b></div>`;
    }
    if (this.subIndicator === 'rsi' && this.data.rsi[index]) {
      extraIndicators += `<div class="hud-item"><span style="color:var(--color-rsi);">RSI(14):</span><b class="hud-val">${this.data.rsi[index].value}</b></div>`;
    }
    if (this.subIndicator === 'macd' && this.data.macd[index]) {
      extraIndicators += `<div class="hud-item"><span style="color:var(--color-macd);">MACD:</span><b class="hud-val">${this.data.macd[index].macd}</b> | Sig: <b class="hud-val">${this.data.macd[index].signal}</b></div>`;
    }

    const priceDisplayHtml = this.priceMode === 'close'
      ? `<div class="hud-item"><span style="color:var(--accent-cyan);">CLOSE:</span><b class="hud-val" style="color:var(--accent-cyan);">$${c.close.toFixed(2)}</b></div>`
      : `
        <div class="hud-item"><span>O:</span><b class="hud-val">${c.open.toFixed(2)}</b></div>
        <div class="hud-item"><span>H:</span><b class="hud-val">${c.high.toFixed(2)}</b></div>
        <div class="hud-item"><span>L:</span><b class="hud-val">${c.low.toFixed(2)}</b></div>
        <div class="hud-item"><span>C:</span><b class="hud-val">${c.close.toFixed(2)}</b></div>
      `;

    const firstCandle = this.data.candles[0];
    const retFromStart = firstCandle && firstCandle.open > 0
      ? (((c.close - firstCandle.open) / firstCandle.open) * 100).toFixed(2)
      : '0.00';
    const retSign = Number(retFromStart) >= 0 ? '+' : '';
    const retColor = Number(retFromStart) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';

    this.hud.innerHTML = `
      <div class="hud-item"><span>TIME:</span><b class="hud-val">${c.time}</b></div>
      ${priceDisplayHtml}
      <div class="hud-item"><span>CHG:</span><b class="hud-val" style="${colorClass}">${change} (${changePct}%)</b></div>
      <div class="hud-item"><span>VOL:</span><b class="hud-val">${(c.volume / 1000000).toFixed(2)}M</b></div>
      <div class="hud-item"><span>PERIOD RET:</span><b class="hud-val" style="color:${retColor};">${retSign}${retFromStart}%</b></div>
      ${extraIndicators}
    `;
  }

  resizeCanvas(canvas, ctx) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    return { width: rect.width, height: rect.height };
  }

  render() {
    if (!this.data || !this.data.candles || this.data.candles.length === 0) return;
    this.renderMainChart();
    if (this.subIndicator && this.subIndicator !== 'none') {
      this.renderSubChart();
    }
  }

  renderMainChart() {
    if (!this.mainCtx) return;
    const { width, height } = this.resizeCanvas(this.mainCanvas, this.mainCtx);
    const ctx = this.mainCtx;
    ctx.clearRect(0, 0, width, height);

    const candles = this.data.candles;
    const n = candles.length;
    const marginRight = 60;
    const marginBottom = 24;
    const plotWidth = width - marginRight;
    const plotHeight = height - marginBottom;

    // Determine Min & Max Price for scaling
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVolume = 0;

    candles.forEach((c) => {
      if (this.priceMode === 'close') {
        if (c.close < minPrice) minPrice = c.close;
        if (c.close > maxPrice) maxPrice = c.close;
      } else {
        if (c.low < minPrice) minPrice = c.low;
        if (c.high > maxPrice) maxPrice = c.high;
      }
      if (c.volume > maxVolume) maxVolume = c.volume;
    });

    // Expand margin
    const pricePadding = (maxPrice - minPrice) * 0.08 || 2;
    minPrice -= pricePadding;
    maxPrice += pricePadding;

    const getY = (price) => plotHeight - ((price - minPrice) / (maxPrice - minPrice)) * plotHeight;
    const getX = (idx) => (idx + 0.5) * (plotWidth / n);
    const candleWidth = Math.max(2, (plotWidth / n) * 0.72);

    // 1. Grid & Price Axis
    ctx.strokeStyle = this.colors.grid;
    ctx.lineWidth = 1;
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.fillStyle = this.colors.text;

    const priceSteps = 5;
    for (let i = 0; i <= priceSteps; i++) {
      const p = minPrice + (i / priceSteps) * (maxPrice - minPrice);
      const y = getY(p);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(plotWidth, y);
      ctx.stroke();
      ctx.fillText(p.toFixed(2), plotWidth + 8, y + 3);
    }

    // Time Axis Marks
    const timeSteps = Math.min(6, n);
    for (let i = 0; i < timeSteps; i++) {
      const idx = Math.floor(i * (n / timeSteps));
      const x = getX(idx);
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, plotHeight);
      ctx.stroke();
      ctx.fillText(candles[idx].time, x - 15, height - 6);
    }

    // 2. Volume Histogram (Subtle bottom bars like Yahoo Finance)
    const volHeight = plotHeight * 0.14;
    candles.forEach((c, idx) => {
      const x = getX(idx);
      const h = (c.volume / maxVolume) * volHeight;
      const y = plotHeight - h;
      ctx.fillStyle = 'rgba(148, 163, 184, 0.22)';
      ctx.fillRect(x - candleWidth / 2, y, candleWidth, h);
    });

    // 3. Bollinger Bands Fill & Lines
    if (this.overlays.bollinger && this.data.bollinger) {
      const bb = this.data.bollinger;
      // Fill
      ctx.fillStyle = this.colors.bbFill;
      ctx.beginPath();
      let started = false;
      bb.forEach((pt, idx) => {
        if (pt.upper !== null && pt.upper !== undefined) {
          const x = getX(idx);
          const y = getY(pt.upper);
          if (!started) { ctx.moveTo(x, y); started = true; } else { ctx.lineTo(x, y); }
        }
      });
      for (let i = bb.length - 1; i >= 0; i--) {
        const pt = bb[i];
        if (pt && pt.lower !== null && pt.lower !== undefined) {
          const x = getX(i);
          const y = getY(pt.lower);
          ctx.lineTo(x, y);
        }
      }
      ctx.closePath();
      ctx.fill();

      // Upper & Lower Lines
      this.drawLineSeries(ctx, bb.map(b => ({ time: b.time, value: b.upper })), getX, getY, this.colors.bbUpper, 1, [3, 3]);
      this.drawLineSeries(ctx, bb.map(b => ({ time: b.time, value: b.lower })), getX, getY, this.colors.bbLower, 1, [3, 3]);
    }

    // 4. Moving Average Overlays
    if (this.overlays.sma20) this.drawLineSeries(ctx, this.data.sma20, getX, getY, this.colors.sma20, 1.8);
    if (this.overlays.sma50) this.drawLineSeries(ctx, this.data.sma50, getX, getY, this.colors.sma50, 1.8);
    if (this.overlays.sma200) this.drawLineSeries(ctx, this.data.sma200, getX, getY, this.colors.sma200, 2.0);
    if (this.overlays.ema20) this.drawLineSeries(ctx, this.data.ema20, getX, getY, this.colors.ema20, 1.5, [4, 4]);

    // 5. Candlesticks (OHLC) OR Close Line Only
    const firstCandle = candles[0];
    const lastCandle = candles[n - 1];
    const isPeriodUp = lastCandle.close >= firstCandle.open;
    const themeColor = isPeriodUp ? this.colors.bullish : this.colors.bearish;

    if (this.priceMode === 'close') {
      // Area Gradient Fill
      const grad = ctx.createLinearGradient(0, 0, 0, plotHeight);
      grad.addColorStop(0, isPeriodUp ? 'rgba(0, 230, 118, 0.22)' : 'rgba(255, 51, 102, 0.22)');
      grad.addColorStop(0.65, isPeriodUp ? 'rgba(0, 230, 118, 0.06)' : 'rgba(255, 51, 102, 0.06)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0.0)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      candles.forEach((c, idx) => {
        const x = getX(idx);
        const y = getY(c.close);
        if (idx === 0) ctx.moveTo(x, plotHeight);
        ctx.lineTo(x, y);
      });
      ctx.lineTo(getX(n - 1), plotHeight);
      ctx.closePath();
      ctx.fill();

      // Horizontal Period Start Baseline (Dashed red line like Yahoo Finance)
      const startY = getY(firstCandle.open);
      ctx.save();
      ctx.strokeStyle = 'rgba(255, 82, 82, 0.4)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, startY);
      ctx.lineTo(plotWidth, startY);
      ctx.stroke();
      ctx.fillStyle = 'rgba(255, 120, 120, 0.7)';
      ctx.font = '9px "JetBrains Mono", monospace';
      ctx.fillText(`START: $${firstCandle.open.toFixed(2)}`, 8, startY - 5);
      ctx.restore();

      // Continuous Smooth Close Line with Two-Tone Segment Coloring (Red below baseline, Green above baseline)
      ctx.save();
      ctx.lineWidth = 2.2;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      for (let i = 0; i < n - 1; i++) {
        const x1 = getX(i);
        const y1 = getY(candles[i].close);
        const x2 = getX(i + 1);
        const y2 = getY(candles[i + 1].close);
        const isSegUp = candles[i + 1].close >= firstCandle.open;
        ctx.strokeStyle = isSegUp ? this.colors.bullish : this.colors.bearish;
        ctx.shadowColor = isSegUp ? 'rgba(0, 230, 118, 0.35)' : 'rgba(255, 51, 102, 0.35)';
        ctx.shadowBlur = 4;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
      ctx.restore();

      // Interactive Cursor Dot (Only drawn on hovered candle like Yahoo Finance)
      if (this.hoverIndex >= 0 && candles[this.hoverIndex]) {
        const hx = getX(this.hoverIndex);
        const hy = getY(candles[this.hoverIndex].close);
        const isHoverUp = candles[this.hoverIndex].close >= firstCandle.open;
        ctx.save();
        ctx.fillStyle = isHoverUp ? this.colors.bullish : this.colors.bearish;
        ctx.shadowColor = ctx.fillStyle;
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(hx, hy, 4.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.8;
        ctx.stroke();
        ctx.restore();
      }
    } else {
      // Candlesticks (Open, High, Low, Close)
      candles.forEach((c, idx) => {
        const x = getX(idx);
        const yOpen = getY(c.open);
        const yClose = getY(c.close);
        const yHigh = getY(c.high);
        const yLow = getY(c.low);
        const isUp = c.close >= c.open;
        const color = isUp ? this.colors.bullish : this.colors.bearish;

        // Wick
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(x, yHigh);
        ctx.lineTo(x, yLow);
        ctx.stroke();

        // Body
        const top = Math.min(yOpen, yClose);
        const bodyH = Math.max(1.5, Math.abs(yClose - yOpen));
        ctx.fillStyle = color;
        ctx.fillRect(x - candleWidth / 2, top, candleWidth, bodyH);
      });
    }

    // 6. Crosshair Line & Dot
    if (this.hoverIndex >= 0 && this.hoverIndex < n) {
      const hx = getX(this.hoverIndex);
      const hc = candles[this.hoverIndex];
      const hy = getY(hc.close);

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;
      
      // Vertical
      ctx.beginPath();
      ctx.moveTo(hx, 0);
      ctx.lineTo(hx, height);
      ctx.stroke();

      // Horizontal
      ctx.beginPath();
      ctx.moveTo(0, hy);
      ctx.lineTo(width, hy);
      ctx.stroke();
      ctx.setLineDash([]);

      // Point
      const dotColor = this.priceMode === 'close'
        ? (hc.close >= firstCandle.open ? this.colors.bullish : this.colors.bearish)
        : (hc.close >= hc.open ? this.colors.bullish : this.colors.bearish);
      ctx.fillStyle = dotColor;
      ctx.beginPath();
      ctx.arc(hx, hy, 4.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // 7. Right Y-Axis Current Price Tag Badge (Yahoo Finance style)
    const curY = getY(lastCandle.close);
    const isDayUp = lastCandle.close >= (candles[n - 2] ? candles[n - 2].close : firstCandle.open);
    const badgeColor = isDayUp ? this.colors.bullish : this.colors.bearish;
    ctx.save();
    ctx.fillStyle = badgeColor;
    const badgeW = 54;
    const badgeH = 18;
    const badgeX = plotWidth + 4;
    const badgeY = Math.max(2, Math.min(plotHeight - badgeH, curY - badgeH / 2));
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 3);
    } else {
      ctx.rect(badgeX, badgeY, badgeW, badgeH);
    }
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(lastCandle.close.toFixed(2), badgeX + badgeW / 2, badgeY + badgeH / 2);
    ctx.restore();
  }

  renderSubChart() {
    if (!this.subCtx) return;
    const { width, height } = this.resizeCanvas(this.subCanvas, this.subCtx);
    const ctx = this.subCtx;
    ctx.clearRect(0, 0, width, height);

    const n = this.data.candles.length;
    const marginRight = 60;
    const marginBottom = 18;
    const plotWidth = width - marginRight;
    const plotHeight = height - marginBottom;
    const getX = (idx) => (idx + 0.5) * (plotWidth / n);

    // Grid
    ctx.strokeStyle = this.colors.grid;
    ctx.lineWidth = 1;
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.fillStyle = this.colors.text;

    if (this.subIndicator === 'rsi') {
      // RSI Bounds (0 - 100)
      const getY = (val) => plotHeight - (val / 100) * plotHeight;

      // 70 & 30 Reference Guides
      ctx.strokeStyle = 'rgba(247, 37, 133, 0.35)';
      ctx.setLineDash([3, 3]);
      [70, 30].forEach((level) => {
        const y = getY(level);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(plotWidth, y);
        ctx.stroke();
        ctx.fillText(level, plotWidth + 8, y + 3);
      });
      ctx.setLineDash([]);

      // Draw RSI Line
      this.drawLineSeries(ctx, this.data.rsi, getX, getY, this.colors.rsi, 2);

    } else if (this.subIndicator === 'macd') {
      // MACD Histogram & Lines
      const macdList = this.data.macd || [];
      let minVal = -1, maxVal = 1;
      macdList.forEach(m => {
        if (m.macd !== null) {
          minVal = Math.min(minVal, m.macd, m.signal, m.hist || 0);
          maxVal = Math.max(maxVal, m.macd, m.signal, m.hist || 0);
        }
      });
      const padding = Math.max(Math.abs(minVal), Math.abs(maxVal)) * 1.2 || 1;
      const getY = (v) => plotHeight / 2 - (v / padding) * (plotHeight / 2);

      // Zero line
      const zeroY = getY(0);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
      ctx.beginPath();
      ctx.moveTo(0, zeroY);
      ctx.lineTo(plotWidth, zeroY);
      ctx.stroke();

      // Histogram Bars
      const barW = Math.max(2, (plotWidth / n) * 0.6);
      macdList.forEach((m, idx) => {
        if (m.hist !== null && m.hist !== undefined) {
          const x = getX(idx);
          const y = getY(m.hist);
          ctx.fillStyle = m.hist >= 0 ? 'rgba(0, 230, 118, 0.6)' : 'rgba(255, 51, 102, 0.6)';
          ctx.fillRect(x - barW / 2, Math.min(zeroY, y), barW, Math.abs(zeroY - y));
        }
      });

      // MACD & Signal Lines
      this.drawLineSeries(ctx, macdList.map(m => ({ value: m.macd })), getX, getY, this.colors.macd, 1.8);
      this.drawLineSeries(ctx, macdList.map(m => ({ value: m.signal })), getX, getY, this.colors.macdSignal, 1.8);

    } else if (this.subIndicator === 'obv') {
      // On-Balance Volume
      const obvList = this.data.obv || [];
      let minVal = Infinity, maxVal = -Infinity;
      obvList.forEach(o => {
        if (o.value !== null) {
          minVal = Math.min(minVal, o.value);
          maxVal = Math.max(maxVal, o.value);
        }
      });
      const diff = maxVal - minVal || 1;
      const getY = (v) => plotHeight - ((v - minVal) / diff) * plotHeight;
      this.drawLineSeries(ctx, obvList, getX, getY, this.colors.obv, 2);
    }
  }

  drawLineSeries(ctx, series, getX, getY, color, lineWidth = 1.5, dash = []) {
    if (!series || series.length === 0) return;
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.setLineDash(dash);
    ctx.beginPath();
    let started = false;

    series.forEach((pt, idx) => {
      if (pt && pt.value !== null && pt.value !== undefined) {
        const x = getX(idx);
        const y = getY(pt.value);
        if (!started) {
          ctx.moveTo(x, y);
          started = true;
        } else {
          ctx.lineTo(x, y);
        }
      }
    });

    ctx.stroke();
    ctx.restore();
  }
}

window.TechnicalChart = TechnicalChart;
