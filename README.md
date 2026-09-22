# eemsdelta2000
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard Eemsdelta</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #0d1117;
      color: #c9d1d9;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    header {
      background-color: #161b22;
      padding: 15px 25px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #30363d;
    }
    header h1 { font-size: 1.5rem; color: #58a6ff; font-weight: 600; }
    #clock { font-size: 1.2rem; font-weight: bold; color: #8b949e; }
    
    .progress-bar-container { width: 100%; height: 4px; background: #21262d; }
    .progress-bar { height: 100%; width: 0%; background: #58a6ff; transition: width 0.1s linear; }

    main { flex: 1; position: relative; padding: 25px; overflow: hidden; }
    .slide {
      position: absolute;
      top: 25px; left: 25px; right: 25px; bottom: 25px;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.6s ease-in-out, visibility 0.6s;
      display: flex;
      flex-direction: column;
    }
    .slide.active { opacity: 1; visibility: visible; }

    .card {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
      margin-bottom: 20px;
    }

    .badge {
      display: inline-block;
      padding: 6px 12px;
      font-weight: bold;
      border-radius: 6px;
      font-size: 0.9rem;
      color: #fff;
    }
    .bg-prio1 { background-color: #da3633; }
    .bg-prio2 { background-color: #d29922; color: #0d1117; }
    .bg-info { background-color: #238636; }

    .weather-temp { font-size: 3.5rem; font-weight: bold; color: #f0f6fc; margin: 10px 0; }
    .grid-forecast { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; }
    .forecast-item { background: #21262d; padding: 12px; border-radius: 8px; text-align: center; }

    nav {
      background: #161b22;
      border-top: 1px solid #30363d;
      display: flex;
      justify-content: center;
      gap: 10px;
      padding: 12px;
    }
    .dot {
      width: 12px; height: 12px;
      border-radius: 50%;
      background: #30363d;
      cursor: pointer;
    }
    .dot.active { background: #58a6ff; }
  </style>
</head>
<body>

  <header>
    <h1>Eemsdelta / Delfzijl Live</h1>
    <div id="clock">--:--:--</div>
  </header>
  <div class="progress-bar-container"><div class="progress-bar" id="progress"></div></div>

  <main>
    <!-- Slide 1: P2000 -->
    <section id="slide-p2000" class="slide active">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
          <h2>P2000 Meldingen Eemsdelta</h2>
          <span id="p2000-prio" class="badge bg-info">Laden...</span>
        </div>
        <p id="p2000-text" style="font-size: 1.2rem; min-height: 50px;">Gegevens worden opgehaald...</p>
        <p id="p2000-time" style="color: #8b949e; margin-top: 10px; font-size: 0.9rem;"></p>
      </div>
    </section>

    <!-- Slide 2: Actueel Weer -->
    <section id="slide-weather" class="slide">
      <div class="card">
        <h2>Actueel Weer Delfzijl</h2>
        <div class="weather-temp" id="current-temp">--°C</div>
        <p id="current-wind">Wind: -- km/h</p>
        <p id="current-rain">Neerslag: -- mm</p>
      </div>
    </section>

    <!-- Slide 3: Weersverwachting -->
    <section id="slide-forecast" class="slide">
      <div class="card">
        <h2>Verwachting komende uren</h2>
        <div class="grid-forecast" id="forecast-container" style="margin-top: 15px;"></div>
      </div>
    </section>

    <!-- Slide 4: Scheepvaart -->
    <section id="slide-shipping" class="slide">
      <div class="card" style="height: 100%;">
        <h2>Scheepvaart Eems / Delfzijl / Eemshaven</h2>
        <div style="margin-top: 15px; background: #011627; border-radius: 8px; padding: 20px; text-align: center; color: #8b949e;">
          <p>📍 <strong>Haven Delfzijl & Eemshaven</strong></p>
          <p style="margin-top: 10px;">Live AIS scheepvaartkaart actief voor het Eems-estuarium.</p>
        </div>
      </div>
    </section>
  </main>

  <nav id="dots-container">
    <div class="dot active" onclick="goToSlide(0)"></div>
    <div class="dot" onclick="goToSlide(1)"></div>
    <div class="dot" onclick="goToSlide(2)"></div>
    <div class="dot" onclick="goToSlide(3)"></div>
  </nav>

  <script>
    const LAT = 53.33;
    const LON = 6.92;
    const slides = ['slide-p2000', 'slide-weather', 'slide-forecast', 'slide-shipping'];
    let currentSlide = 0;
    let progressInterval;

    function updateClock() {
      const now = new Date();
      document.getElementById('clock').innerText = now.toLocaleTimeString('nl-NL');
    }
    setInterval(updateClock, 1000);
    updateClock();

    function showSlide(index) {
      slides.forEach((id, idx) => {
        const el = document.getElementById(id);
        const dot = document.querySelectorAll('.dot')[idx];
        if (el) el.classList.toggle('active', idx === index);
        if (dot) dot.classList.toggle('active', idx === index);
      });
      currentSlide = index;
      resetProgressBar();
    }

    function nextSlide() {
      showSlide((currentSlide + 1) % slides.length);
    }

    function goToSlide(index) {
      showSlide(index);
    }

    function resetProgressBar() {
      clearInterval(progressInterval);
      const progressBar = document.getElementById('progress');
      let width = 0;
      progressInterval = setInterval(() => {
        width += 1;
        if (progressBar) progressBar.style.width = width + '%';
        if (width >= 100) {
          clearInterval(progressInterval);
          nextSlide();
        }
      }, 80);
    }

    async function fetchP2000() {
      try {
        const res = await fetch("https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Ffeed.alarmeringen.nl%2Feemsdelta.rss");
        const data = await res.json();
        if (data.status === 'ok' && data.items && data.items.length > 0) {
          const item = data.items[0];
          document.getElementById('p2000-text').innerText = item.title;
          document.getElementById('p2000-time').innerText = new Date(item.pubDate).toLocaleString('nl-NL');

          const prioBadge = document.getElementById('p2000-prio');
          if (item.title.includes('Prio 1') || item.title.includes('A1')) {
            prioBadge.innerText = 'PRIO 1 / SPOED';
            prioBadge.className = 'badge bg-prio1';
          } else if (item.title.includes('Prio 2') || item.title.includes('A2')) {
            prioBadge.innerText = 'PRIO 2';
            prioBadge.className = 'badge bg-prio2';
          } else {
            prioBadge.innerText = 'INFO';
            prioBadge.className = 'badge bg-info';
          }
        }
      } catch (e) {
        document.getElementById('p2000-text').innerText = "Geen actuele meldingen beschikbaar.";
      }
    }

    async function fetchWeather() {
      try {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,rain,wind_speed_10m&hourly=temperature_2m,precipitation_probability&forecast_days=2&timezone=auto`;
        const res = await fetch(url);
        const data = await res.json();

        if (data.current) {
          document.getElementById('current-temp').innerText = `${Math.round(data.current.temperature_2m)}°C`;
          document.getElementById('current-wind').innerText = `Wind: ${Math.round(data.current.wind_speed_10m)} km/h`;
          document.getElementById('current-rain').innerText = `Neerslag: ${data.current.rain} mm`;
        }

        const grid = document.getElementById('forecast-container');
        if (grid && data.hourly) {
          grid.innerHTML = '';
          const nowHour = new Date().getHours();
          for (let i = 0; i < 6; i++) {
            const idx = nowHour + (i * 3);
            if (data.hourly.time[idx]) {
              const time = new Date(data.hourly.time[idx]).getHours() + ':00';
              const temp = Math.round(data.hourly.temperature_2m[idx]);
              const pop = data.hourly.precipitation_probability[idx];
              grid.innerHTML += `
                <div class="forecast-item">
                  <div>${time}</div>
                  <div style="font-size:1.4rem; font-weight:bold; margin: 4px 0;">${temp}°C</div>
                  <div style="color:#8b949e; font-size:0.8rem;">💧 ${pop}%</div>
                </div>
              `;
            }
          }
        }
      } catch (e) {
        console.error("Weer ophalen mislukt:", e);
      }
    }

    fetchP2000();
    fetchWeather();
    resetProgressBar();
    setInterval(fetchP2000, 30000);
    setInterval(fetchWeather, 600000);
  </script>
</body>
</html>
