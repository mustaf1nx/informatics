/* EduCon Progress & Leaderboard module
   by Azamat

   Работает "из коробки" без бэкенда: прогресс и ник хранятся в localStorage
   браузера ученика (тест помнит его результат при повторном заходе).

   Если хочешь настоящий общий рейтинг между учениками (топ на сайте, видимый
   всем) - подними простой backend endpoint (пример на FastAPI лежит в файле
   backend_leaderboard_example.py) и впиши его адрес в API_BASE ниже.
   Пока API_BASE пустой - модуль работает только локально, раздел "Топ"
   на хаб-странице покажет только результаты этого устройства.
*/

const EduConProgress = (function () {
  const STORAGE_KEY = 'educon_progress_v1';
  const NICK_KEY = 'educon_nickname_v1';

  // Впиши сюда адрес своего backend, например 'https://zeinacademy.up.railway.app'
  // Оставь пустой строкой, если backend пока не поднят.
  const API_BASE = '';

  function loadAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function saveAll(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) { /* тихо игнорируем, если localStorage недоступен */ }
  }

  function getNickname() {
    try {
      return localStorage.getItem(NICK_KEY) || '';
    } catch (e) {
      return '';
    }
  }

  function setNickname(name) {
    try {
      localStorage.setItem(NICK_KEY, name.trim().slice(0, 30));
    } catch (e) { /* ignore */ }
  }

  function ensureNickname() {
    let name = getNickname();
    if (!name) {
      name = prompt('Как тебя записать в рейтинг? Введи имя:', '') || 'Аноним';
      setNickname(name);
    }
    return name;
  }

  function recordResult(testId, testTitle, score, total) {
    const all = loadAll();
    const prev = all[testId] || { best: 0, total: total, attempts: 0, history: [] };
    const isNewBest = score > prev.best;
    const entry = {
      testId: testId,
      title: testTitle,
      best: Math.max(prev.best, score),
      total: total,
      attempts: (prev.attempts || 0) + 1,
      lastScore: score,
      lastDate: new Date().toISOString()
    };
    all[testId] = entry;
    saveAll(all);

    // Пытаемся отправить на общий backend, если он настроен
    if (API_BASE) {
      const nickname = getNickname();
      if (nickname) {
        fetch(API_BASE + '/api/leaderboard', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nickname: nickname,
            test_id: testId,
            test_title: testTitle,
            score: score,
            total: total
          })
        }).catch(function () { /* нет связи с сервером - молча пропускаем */ });
      }
    }

    return { entry: entry, isNewBest: isNewBest };
  }

  function getProgress() {
    return loadAll();
  }

  function getOverallStats(testIds) {
    const all = loadAll();
    let completed = 0;
    let sumPct = 0;
    testIds.forEach(function (id) {
      if (all[id]) {
        completed++;
        sumPct += (all[id].best / all[id].total) * 100;
      }
    });
    return {
      completed: completed,
      totalTests: testIds.length,
      avgPct: completed ? Math.round(sumPct / completed) : 0
    };
  }

  async function fetchLeaderboard(testId) {
    if (API_BASE) {
      try {
        const res = await fetch(API_BASE + '/api/leaderboard' + (testId ? ('?test_id=' + encodeURIComponent(testId)) : ''));
        if (res.ok) {
          const data = await res.json();
          return { source: 'server', rows: data };
        }
      } catch (e) { /* fall through to local */ }
    }
    // Локальный fallback: показываем только результаты этого устройства
    const all = loadAll();
    const rows = [];
    const nickname = getNickname() || 'Ты';
    Object.keys(all).forEach(function (id) {
      if (!testId || id === testId) {
        const e = all[id];
        rows.push({
          nickname: nickname,
          test_id: id,
          test_title: e.title,
          score: e.best,
          total: e.total,
          pct: Math.round((e.best / e.total) * 100)
        });
      }
    });
    rows.sort(function (a, b) { return b.pct - a.pct; });
    return { source: 'local', rows: rows };
  }

  return {
    ensureNickname: ensureNickname,
    getNickname: getNickname,
    setNickname: setNickname,
    recordResult: recordResult,
    getProgress: getProgress,
    getOverallStats: getOverallStats,
    fetchLeaderboard: fetchLeaderboard,
    API_BASE: API_BASE
  };
})();
