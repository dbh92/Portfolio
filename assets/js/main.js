/* HọcFree.vn – main.js */
(function () {
  "use strict";

  var doc = document.documentElement;
  var ROOT = doc.getAttribute("data-root") || "";
  var POSTS = window.HF_POSTS || [];
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };

  /* ---------- Giao diện sáng / tối ---------- */
  var themeBtn = $(".theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var dark = doc.classList.toggle("dark");
      try { localStorage.setItem("hf-theme", dark ? "dark" : "light"); } catch (e) { /* bỏ qua */ }
    });
  }

  /* ---------- Menu chính: mega menu, dropdown, drawer ---------- */
  var header = $(".site-header");
  var nav = $(".site-nav");
  var burger = $(".burger");
  var scrim = $(".nav-scrim");
  var navItems = $$(".nav-item.has-panel");
  var desktop = window.matchMedia("(min-width: 1061px)");
  var canHover = window.matchMedia("(hover: hover) and (pointer: fine)");
  var hoverTimer = null;
  var hoverOpenedAt = 0;

  function trigger(li) { return $(".nav-trigger", li); }
  function closeItem(li) {
    li.classList.remove("is-open");
    trigger(li).setAttribute("aria-expanded", "false");
  }
  function openItem(li) {
    navItems.forEach(function (other) { if (other !== li) closeItem(other); });
    li.classList.add("is-open");
    trigger(li).setAttribute("aria-expanded", "true");
  }
  function closeAll() { navItems.forEach(closeItem); }
  function openItemEl() { return navItems.filter(function (li) { return li.classList.contains("is-open"); })[0]; }

  navItems.forEach(function (li) {
    var btn = trigger(li);
    btn.addEventListener("click", function () {
      // Vừa mở bằng hover thì cú click ngay sau đó không đóng lại
      if (li.classList.contains("is-open") && Date.now() - hoverOpenedAt > 400) closeItem(li);
      else openItem(li);
    });
    btn.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown" && desktop.matches) {
        ev.preventDefault();
        openItem(li);
        var first = $(".nav-panel a", li);
        if (first) first.focus();
      }
    });
    // Hover có độ trễ nhỏ để đi chuột ngang qua menu không làm panel nhấp nháy
    li.addEventListener("mouseenter", function () {
      if (!desktop.matches || !canHover.matches) return;
      clearTimeout(hoverTimer);
      var delay = openItemEl() ? 0 : 90;
      hoverTimer = setTimeout(function () { openItem(li); hoverOpenedAt = Date.now(); }, delay);
    });
    li.addEventListener("mouseleave", function () {
      if (!desktop.matches || !canHover.matches) return;
      clearTimeout(hoverTimer);
      hoverTimer = setTimeout(function () { closeItem(li); }, 180);
    });
    li.addEventListener("focusout", function (ev) {
      if (desktop.matches && !li.contains(ev.relatedTarget)) closeItem(li);
    });
  });

  document.addEventListener("click", function (ev) {
    if (desktop.matches && nav && !nav.contains(ev.target)) closeAll();
  });

  function setDrawer(open) {
    if (!nav) return;
    nav.classList.toggle("open", open);
    doc.classList.toggle("nav-open", open);
    if (scrim) scrim.hidden = !open;
    if (burger) burger.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      var active = navItems.filter(function (li) { return trigger(li).classList.contains("is-active"); })[0];
      if (active) openItem(active);
      $(".nav-close", nav).focus();
    } else {
      closeAll();
    }
  }
  if (burger) burger.addEventListener("click", function () { setDrawer(!nav.classList.contains("open")); });
  if (scrim) scrim.addEventListener("click", function () { setDrawer(false); });
  var navClose = nav && $(".nav-close", nav);
  if (navClose) navClose.addEventListener("click", function () { setDrawer(false); if (burger) burger.focus(); });
  desktop.addEventListener && desktop.addEventListener("change", function () { setDrawer(false); });

  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    var li = openItemEl();
    if (nav && nav.classList.contains("open")) {
      setDrawer(false);
      if (burger) burger.focus();
    } else if (li) {
      closeItem(li);
      trigger(li).focus();
    }
  });

  /* ---------- Tìm kiếm ---------- */
  var TOPICS = window.HF_TOPICS || [];
  var ICON_TOPIC = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>';
  function normalize(s) {
    return (s || "").toLowerCase().replace(/đ/g, "d")
      .normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function search(q) {
    var terms = normalize(q).split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    return POSTS.map(function (p) {
      var title = normalize(p.t);
      var hay = title + " " + normalize(p.e) + " " + normalize(p.tags.join(" ")) + " " + normalize(p.cn);
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        if (hay.indexOf(terms[i]) === -1) return null;
        score += title.indexOf(terms[i]) !== -1 ? 3 : 1;
      }
      return { p: p, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; })
      .map(function (r) { return r.p; });
  }
  function searchTopics(q) {
    var terms = normalize(q).split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    return TOPICS.filter(function (t) {
      var hay = normalize(t.t + " " + t.s + " " + t.g);
      return terms.every(function (term) { return hay.indexOf(term) !== -1; });
    }).sort(function (a, b) {
      // Ưu tiên lộ trình flagship, tên bắt đầu bằng từ khóa, lộ trình, rồi chủ đề có nhiều bài
      var qa = normalize(a.t).indexOf(terms[0]) === 0 ? 1 : 0;
      var qb = normalize(b.t).indexOf(terms[0]) === 0 ? 1 : 0;
      return ((b.f || 0) - (a.f || 0)) || (qb - qa) || ((b.n < 0) - (a.n < 0)) || (b.n - a.n);
    });
  }
  function topicMeta(t) {
    if (t.n < 0) return "Learning Path · " + escapeHtml(t.g);
    var where = escapeHtml(t.s) + (t.g ? " › " + escapeHtml(t.g) : "");
    return where + " · " + (t.n ? t.n + " bài" : "đang biên soạn");
  }
  function highlight(text, q) {
    var safe = escapeHtml(text);
    var terms = q.trim().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return safe;
    var re = new RegExp("(" + terms.map(function (t) {
      return escapeHtml(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }).join("|") + ")", "gi");
    return safe.replace(re, "<mark>$1</mark>");
  }

  var dialog = $(".search-dialog");
  var dInput = dialog && $("input", dialog);
  var suggest = dialog && $(".search-suggest", dialog);
  var emptyHtml = suggest ? suggest.innerHTML : "";
  var lastFocus = null;

  function openSearch() {
    if (!dialog) return;
    if (nav && nav.classList.contains("open")) setDrawer(false);
    closeAll();
    lastFocus = document.activeElement;
    dialog.hidden = false;
    doc.classList.add("nav-open");
    dInput.focus();
    dInput.select();
  }
  function closeSearch() {
    if (!dialog || dialog.hidden) return;
    dialog.hidden = true;
    doc.classList.remove("nav-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function renderSuggest() {
    var q = dInput.value.trim();
    if (!q) { suggest.innerHTML = emptyHtml; return; }
    var topics = searchTopics(q).slice(0, 5);
    var posts = search(q).slice(0, 6);
    var html = "";
    if (topics.length) {
      html += '<p class="search-group-title">Chủ đề & lộ trình</p>' + topics.map(function (t) {
        return '<a class="search-item" href="' + ROOT + t.u + '"><span class="search-ico">' + (t.n < 0 ? "⭐" : ICON_TOPIC) + "</span>" +
          "<span>" + highlight(t.t, q) + "<small>" + topicMeta(t) + "</small></span></a>";
      }).join("");
    }
    if (posts.length) {
      html += '<p class="search-group-title">Bài viết</p>' + posts.map(function (p) {
        return '<a class="search-item" href="' + ROOT + p.u + '"><img src="' + ROOT + p.img + '" alt="" loading="lazy">' +
          "<span>" + highlight(p.t, q) + "<small>" + escapeHtml(p.cn) + " · " + p.d + "</small></span></a>";
      }).join("");
    }
    suggest.innerHTML = html || '<p class="empty">Không tìm thấy kết quả cho “' + escapeHtml(q) + '”. Nhấn Enter để tìm kỹ hơn.</p>';
  }
  function moveFocus(step) {
    var links = $$(".search-item, .chip", suggest);
    if (!links.length) return;
    var cur = links.indexOf($(".focus", suggest));
    if (cur > -1) links[cur].classList.remove("focus");
    var next = cur + step;
    if (next < 0) next = links.length - 1;
    if (next >= links.length) next = 0;
    links[next].classList.add("focus");
    links[next].scrollIntoView({ block: "nearest" });
  }

  if (dialog) {
    $$(".search-open").forEach(function (b) { b.addEventListener("click", openSearch); });
    $(".search-close", dialog).addEventListener("click", closeSearch);
    $(".search-scrim", dialog).addEventListener("click", closeSearch);
    dInput.addEventListener("input", renderSuggest);
    dInput.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown") { ev.preventDefault(); moveFocus(1); }
      else if (ev.key === "ArrowUp") { ev.preventDefault(); moveFocus(-1); }
      else if (ev.key === "Enter") {
        var f = $(".focus", suggest);
        if (f) { ev.preventDefault(); location.href = f.href; }
      }
    });
    // Giữ Tab trong hộp thoại
    dialog.addEventListener("keydown", function (ev) {
      if (ev.key !== "Tab") return;
      var f = $$("input, button, a[href]", dialog).filter(function (el) { return el.offsetParent !== null; });
      if (!f.length) return;
      if (ev.shiftKey && document.activeElement === f[0]) { ev.preventDefault(); f[f.length - 1].focus(); }
      else if (!ev.shiftKey && document.activeElement === f[f.length - 1]) { ev.preventDefault(); f[0].focus(); }
    });
    document.addEventListener("keydown", function (ev) {
      var tag = (ev.target.tagName || "").toLowerCase();
      var typing = tag === "input" || tag === "textarea" || ev.target.isContentEditable;
      if (ev.key === "Escape" && !dialog.hidden) { ev.stopImmediatePropagation(); closeSearch(); }
      else if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k") { ev.preventDefault(); dialog.hidden ? openSearch() : closeSearch(); }
      else if (ev.key === "/" && !typing && dialog.hidden) { ev.preventDefault(); openSearch(); }
    }, true);
    var kbd = $(".search-trigger kbd");
    if (kbd && /Mac|iPhone|iPad/.test(navigator.platform || "")) kbd.textContent = "⌘K";
  }

  /* Header đổ bóng nhẹ khi cuộn */
  function onHeaderScroll() { if (header) header.classList.toggle("scrolled", window.scrollY > 4); }
  window.addEventListener("scroll", onHeaderScroll, { passive: true });
  onHeaderScroll();

  /* Trang search.html */
  var results = $("#search-results");
  if (results) {
    var q = new URLSearchParams(location.search).get("q") || "";
    var input = $("#search-page-input");
    var summary = $("#search-summary");
    input.value = q;
    var list = q ? search(q) : POSTS;
    var topicCount = q ? searchTopics(q).length : 0;
    summary.textContent = q
      ? (list.length ? "Tìm thấy " + list.length + " bài viết cho “" + q + "”"
        : topicCount ? "Chưa có bài viết cho “" + q + "”, nhưng có các chủ đề liên quan:"
        : "Không có kết quả cho “" + q + "”. Hãy thử từ khóa khác.")
      : (POSTS.length ? "Tất cả " + POSTS.length + " bài viết" : "Chưa có bài viết nào. Hãy bắt đầu từ các chủ đề trong menu hoặc Learning Paths.");
    if (q) document.title = "Tìm: " + q + " | HọcFree";
    var topicHits = q ? searchTopics(q).slice(0, 8) : [];
    if (topicHits.length) {
      var box = document.createElement("div");
      box.className = "search-topics chips";
      box.innerHTML = topicHits.map(function (t) {
        return '<a class="chip" href="' + ROOT + t.u + '">' + (t.n < 0 ? "⭐ " : "") + escapeHtml(t.t) +
          "<small>" + (t.n < 0 ? "Learning Path" : escapeHtml(t.s)) + "</small></a>";
      }).join("");
      results.parentNode.insertBefore(box, results);
    }
    results.innerHTML = list.map(function (p) {
      var url = ROOT + p.u;
      return '<article class="post-row">' +
        '<a class="thumb" href="' + url + '" tabindex="-1" aria-hidden="true"><img src="' + ROOT + p.img + '" alt="" loading="lazy"></a>' +
        '<div class="post-row-body"><a class="kicker cat-' + p.c + '" href="' + ROOT + p.c + '/index.html">' + escapeHtml(p.cn) + "</a>" +
        '<h3><a href="' + url + '">' + highlight(p.t, q) + "</a></h3>" +
        "<p>" + highlight(p.e, q) + "</p>" +
        '<div class="meta"><span>' + p.d + "</span><span>" + p.m + " phút đọc</span></div></div></article>";
    }).join("");
  }

  /* ---------- Learning Path: tiến độ (lưu trên trình duyệt) ---------- */
  var pathPage = $("[data-path]");
  if (pathPage) {
    var storeKey = "hf-path-" + pathPage.getAttribute("data-path");
    var steps = $$(".step", pathPage);
    var done = {};
    try { (JSON.parse(localStorage.getItem(storeKey)) || []).forEach(function (s) { done[s] = true; }); } catch (e) { /* bỏ qua */ }

    var renderPath = function () {
      var count = 0, current = null;
      steps.forEach(function (li) {
        var slug = li.getAttribute("data-step");
        var isDone = !!done[slug];
        if (isDone) count++;
        else if (!current) current = li;
        li.classList.toggle("is-done", isDone);
        $("[data-step-check]", li).checked = isDone;
      });
      steps.forEach(function (li) {
        var slug = li.getAttribute("data-step");
        li.classList.toggle("is-current", li === current);
        var link = $('[data-map-step="' + slug + '"]', pathPage);
        if (link) {
          link.classList.toggle("is-done", !!done[slug]);
          link.classList.toggle("is-current", li === current);
        }
      });
      $("[data-progress-text]", pathPage).textContent = count + "/" + steps.length + " chặng";
      $("[data-progress-bar]", pathPage).style.width = (count / steps.length * 100) + "%";
      var cta = $("[data-path-continue]", pathPage);
      if (cta && count) {
        if (current) {
          cta.href = "#" + current.id;
          cta.textContent = "Tiếp tục: Chặng " + (steps.indexOf(current) + 1) + " · " + $("h3", current).lastChild.textContent;
        } else {
          cta.href = "#muc-tieu";
          cta.textContent = "Bạn đã hoàn thành lộ trình 🎯";
        }
      }
    };

    pathPage.addEventListener("change", function (ev) {
      var slug = ev.target.getAttribute("data-step-check");
      if (!slug) return;
      if (ev.target.checked) done[slug] = true; else delete done[slug];
      try { localStorage.setItem(storeKey, JSON.stringify(Object.keys(done))); } catch (e) { /* bỏ qua */ }
      renderPath();
    });
    renderPath();
  }

  /* ---------- Bài viết: bảng, nút copy code, tiến độ đọc ---------- */
  $$(".prose table").forEach(function (t) {
    var wrap = document.createElement("div");
    wrap.className = "table-wrap";
    t.parentNode.insertBefore(wrap, t);
    wrap.appendChild(t);
  });

  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
    } else { fallbackCopy(text); done(); }
  }
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) { /* bỏ qua */ }
    document.body.removeChild(ta);
  }

  $$(".prose pre").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "Sao chép";
    btn.addEventListener("click", function () {
      copyText(pre.querySelector("code").innerText, function () {
        btn.textContent = "Đã chép ✓";
        setTimeout(function () { btn.textContent = "Sao chép"; }, 1600);
      });
    });
    pre.appendChild(btn);
  });

  $$(".copy-link").forEach(function (btn) {
    btn.addEventListener("click", function () {
      copyText(btn.getAttribute("data-url"), function () {
        btn.classList.add("copied");
        setTimeout(function () { btn.classList.remove("copied"); }, 1600);
      });
    });
  });

  var progress = $(".progress");
  var article = $(".prose");
  var toTop = $(".to-top");
  function onScroll() {
    var y = window.scrollY;
    if (progress && article) {
      var rect = article.getBoundingClientRect();
      var total = article.offsetHeight - window.innerHeight + 200;
      var pct = Math.min(100, Math.max(0, (-rect.top + 200) / total * 100));
      progress.style.width = pct + "%";
    }
    if (toTop) toTop.classList.toggle("show", y > 600);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0 }); });
})();
