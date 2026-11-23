/* ==========================================================================
   Eke · lógica de la tienda (sin dependencias)
   Carrito, inventario, favoritos, checkout, mesa de ayuda (ITIL),
   seguimiento, cuenta, búsqueda, eventos de Google Analytics 4 y Web Vitals.
   ========================================================================== */
(function () {
  'use strict';

  var BASE = document.documentElement.getAttribute('data-base') || '';
  var CAT = window.EKE_CATALOG || { products: [], categories: {}, shipping: [] };
  var P = {};
  CAT.products.forEach(function (p) { P[p.slug] = p; });

  /* ------------------------------------------------------------ utilidades */
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function url(p) { return BASE + p; }
  function img(name) { return url('/assets/img/' + name + '.webp'); }
  function fmt(n) { return '$' + Number(n).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' MXN'; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function icon(n) { return '<svg class="icon" aria-hidden="true"><use href="#i-' + n + '"></use></svg>'; }
  function params() { return new URLSearchParams(location.search); }
  function rand(n) { var s = ''; for (var i = 0; i < n; i++) s += Math.floor(Math.random() * 10); return s; }
  function today() { var d = new Date(); return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0'); }
  function dateStr(iso) { return new Date(iso).toLocaleString('es-MX', { dateStyle: 'medium', timeStyle: 'short' }); }

  var store = {
    get: function (k, d) { try { var v = localStorage.getItem('eke_' + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem('eke_' + k, JSON.stringify(v)); } catch (e) { /* almacenamiento no disponible */ } }
  };

  /* ------------------------------------------------------------ analítica (GA4) */
  function track(name, data) {
    data = data || {};
    if (typeof window.gtag === 'function') window.gtag('event', name, data);
    if (store.get('debug', false)) console.info('[GA4]', name, data);
  }
  function gaItem(slug, qty) {
    var p = P[slug];
    return { item_id: p.sku, item_name: p.name, item_category: CAT.categories[p.category], price: p.price, quantity: qty || 1 };
  }

  /* ------------------------------------------------------------ toast */
  var toastTimer;
  function toast(html) {
    var t = $('.toast');
    if (!t) return;
    t.innerHTML = html;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.hidden = true; }, 3800);
  }

  /* ------------------------------------------------------------ inventario */
  function sold() { return store.get('sold', {}); }
  function available(slug) { return P[slug] ? Math.max(0, P[slug].stock - (sold()[slug] || 0)) : 0; }
  function renderStock() {
    $$('[data-stock-for]').forEach(function (el) {
      var slug = el.getAttribute('data-stock-for');
      var n = available(slug);
      var scope = el.closest('[data-product], [data-product-page]') || document;
      var btns = $$('[data-add-to-cart="' + slug + '"], [data-buy-now="' + slug + '"]', scope);
      if (n <= 0) {
        el.textContent = 'Agotado';
        el.className = 'stock out';
        btns.forEach(function (b) { b.setAttribute('aria-disabled', 'true'); if (b.tagName === 'BUTTON') b.disabled = true; });
      } else if (n <= 10) {
        el.textContent = '¡Quedan solo ' + n + '!';
        el.className = 'stock low';
      } else {
        el.textContent = 'Disponible';
        el.className = 'stock';
      }
    });
  }

  /* ------------------------------------------------------------ carrito */
  function getCart() { return store.get('cart', []).filter(function (i) { return P[i.slug] && i.qty > 0; }); }
  function setCart(c) { store.set('cart', c); renderHeader(); }
  function shippingFor(id, subtotal) {
    var s = CAT.shipping.filter(function (x) { return x.id === id; })[0] || CAT.shipping[0];
    var cost = s.free_from && subtotal >= s.free_from ? 0 : s.cost;
    return { id: s.id, label: s.label, cost: cost, free_from: s.free_from };
  }
  function totals(cart, shipId) {
    var subtotal = cart.reduce(function (t, i) { return t + P[i.slug].price * i.qty; }, 0);
    var ship = shipId ? shippingFor(shipId, subtotal) : null;
    return { subtotal: subtotal, ship: ship, total: subtotal + (ship ? ship.cost : 0), count: cart.reduce(function (t, i) { return t + i.qty; }, 0) };
  }
  function addToCart(slug, qty, silent) {
    var cart = getCart();
    var line = cart.filter(function (i) { return i.slug === slug; })[0];
    var current = line ? line.qty : 0;
    var max = available(slug);
    var next = Math.min(current + qty, max);
    if (next <= current) {
      toast(max <= 0 ? 'Producto agotado.' : 'Solo hay ' + max + ' piezas disponibles.');
      return false;
    }
    if (line) line.qty = next; else cart.push({ slug: slug, qty: next });
    setCart(cart);
    track('add_to_cart', { currency: 'MXN', value: P[slug].price * (next - current), items: [gaItem(slug, next - current)] });
    if (!silent) toast(icon('check') + ' ' + esc(P[slug].name) + ' agregado. <a href="' + url('/carrito/') + '">Ver carrito</a>');
    return true;
  }
  function renderHeader() {
    var t = totals(getCart());
    $$('[data-cart-count]').forEach(function (el) { el.textContent = t.count; });
    $$('[data-cart-total]').forEach(function (el) { el.textContent = fmt(t.subtotal); });
    var s = store.get('session', null);
    var name = $('[data-account-name]'), sub = $('[data-account-sub]');
    if (s && name) { name.textContent = 'Hola, ' + s.name.split(' ')[0]; sub.textContent = 'Mi cuenta'; }
  }

  /* ------------------------------------------------------------ favoritos */
  function favs() { return store.get('favs', []); }
  function renderFavs() {
    var f = favs();
    $$('[data-fav]').forEach(function (b) { b.setAttribute('aria-pressed', f.indexOf(b.getAttribute('data-fav')) >= 0 ? 'true' : 'false'); });
  }
  function toggleFav(slug) {
    var f = favs(), i = f.indexOf(slug);
    if (i >= 0) { f.splice(i, 1); toast('Quitado de favoritos.'); }
    else { f.push(slug); toast(icon('heart') + ' Guardado en <a href="' + url('/favoritos/') + '">favoritos</a>.'); track('add_to_wishlist', { currency: 'MXN', value: P[slug].price, items: [gaItem(slug)] }); }
    store.set('favs', f);
    renderFavs();
  }

  /* ------------------------------------------------------------ eventos globales */
  document.addEventListener('click', function (e) {
    var t = e.target.closest('button, a');
    if (!t) return;

    if (t.hasAttribute('data-add-to-cart')) {
      if (t.disabled) return;
      var slug = t.getAttribute('data-add-to-cart'), qty = 1;
      if (t.hasAttribute('data-with-qty')) {
        var inp = $('[data-qty-input]', t.closest('[data-product-page]'));
        qty = Math.max(1, parseInt(inp && inp.value, 10) || 1);
      }
      addToCart(slug, qty);
      return;
    }
    if (t.hasAttribute('data-buy-now')) {
      e.preventDefault();
      if (t.getAttribute('aria-disabled') === 'true') return;
      var s2 = t.getAttribute('data-buy-now');
      var qi = $('[data-qty-input]');
      var inCart = getCart().some(function (i) { return i.slug === s2; });
      if (!inCart) addToCart(s2, Math.max(1, parseInt(qi && qi.value, 10) || 1), true);
      location.href = url('/carrito/');
      return;
    }
    if (t.hasAttribute('data-fav')) { e.preventDefault(); toggleFav(t.getAttribute('data-fav')); return; }
    if (t.hasAttribute('data-qty-step')) {
      var input = $('[data-qty-input]', t.closest('[data-qty]'));
      input.value = Math.max(1, (parseInt(input.value, 10) || 1) + parseInt(t.getAttribute('data-qty-step'), 10));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      return;
    }
    if (t.hasAttribute('data-share')) {
      var method = t.getAttribute('data-share');
      var box = t.closest('[data-share-url]');
      if (method === 'native' && navigator.share) {
        e.preventDefault();
        navigator.share({ title: box.getAttribute('data-share-title'), url: box.getAttribute('data-share-url') }).catch(function () {});
      }
      track('share', { method: method, content_type: 'page', item_id: location.pathname });
      return;
    }
    if (t.hasAttribute('data-track')) {
      track(t.getAttribute('data-track'), { network: t.getAttribute('data-network') || undefined, platform: t.getAttribute('data-platform') || undefined, page: location.pathname });
    }
    if (t.classList.contains('video-facade') && t.closest('[data-youtube]')) {
      var fig = t.closest('[data-youtube]');
      var id = fig.getAttribute('data-youtube');
      var ifr = document.createElement('iframe');
      ifr.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
      ifr.title = t.getAttribute('aria-label');
      ifr.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';
      ifr.allowFullscreen = true;
      t.replaceWith(ifr);
      track('video_start', { video_title: ifr.title, video_provider: 'youtube' });
      return;
    }
    if (t.classList.contains('sub-toggle')) {
      var li = t.closest('.has-sub');
      var open = li.classList.toggle('open');
      t.setAttribute('aria-expanded', open);
      return;
    }
    if (t.classList.contains('menu-toggle')) {
      var nav = $('#main-nav');
      var o = nav.classList.toggle('open');
      t.setAttribute('aria-expanded', o);
      t.innerHTML = icon(o ? 'close' : 'menu').replace('class="icon"', 'class="icon icon-lg"');
    }
  });

  /* ------------------------------------------------------------ carrusel del hero */
  function initCarousel() {
    var root = $('[data-carousel]');
    if (!root) return;
    var slides = $$('[data-slide]', root), dots = $$('[data-dot]'), i = 0, timer;
    function show(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      dots.forEach(function (d, k) { d.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
    }
    function start() {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      stop(); timer = setInterval(function () { show(i + 1); }, 6000);
    }
    function stop() { clearInterval(timer); }
    dots.forEach(function (d) { d.addEventListener('click', function () { show(+d.getAttribute('data-dot')); start(); }); });
    var hero = root.closest('.hero');
    hero.addEventListener('mouseenter', stop);
    hero.addEventListener('mouseleave', start);
    hero.addEventListener('focusin', stop);
    start();
  }

  /* ------------------------------------------------------------ búsqueda y orden del catálogo */
  function initCatalog() {
    var wrap = $('[data-filterable]');
    if (!wrap) return;
    var grid = $('.grid', wrap);
    var cards = $$('[data-product]', grid);
    var original = cards.slice();
    var q = (params().get('q') || '').trim();
    var sortSel = $('[data-sort]');
    var searchInput = $('#q');
    if (searchInput && q) searchInput.value = q;

    function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
    function apply() {
      var terms = norm(q).split(/\s+/).filter(Boolean);
      var visible = 0;
      cards.forEach(function (c) {
        var p = P[c.getAttribute('data-product')];
        var hay = norm(p.name + ' ' + p.short + ' ' + CAT.categories[p.category]);
        var ok = terms.every(function (t) { return hay.indexOf(t) >= 0; });
        c.hidden = !ok;
        if (ok) visible++;
      });
      var mode = sortSel ? sortSel.value : '';
      var sorted = original.slice();
      if (mode === 'price-asc') sorted.sort(function (a, b) { return a.dataset.price - b.dataset.price; });
      if (mode === 'price-desc') sorted.sort(function (a, b) { return b.dataset.price - a.dataset.price; });
      if (mode === 'name') sorted.sort(function (a, b) { return a.dataset.name.localeCompare(b.dataset.name, 'es'); });
      sorted.forEach(function (c) { grid.appendChild(c); });
      var res = $('[data-results]');
      if (res) res.textContent = visible + (visible === 1 ? ' producto' : ' productos');
      var label = $('[data-search-label]');
      if (label && q) label.textContent = 'Resultados para “' + q + '”.';
      var empty = $('[data-empty]');
      if (empty) empty.hidden = visible > 0;
    }
    if (sortSel) sortSel.addEventListener('change', apply);
    apply();
    if (q) track('search', { search_term: q });
    track('view_item_list', { item_list_name: document.title, items: cards.map(function (c) { return gaItem(c.getAttribute('data-product')); }) });
  }

  function initProductPage() {
    var page = $('[data-product-page]');
    if (!page) return;
    var slug = page.getAttribute('data-product-page');
    track('view_item', { currency: 'MXN', value: P[slug].price, items: [gaItem(slug)] });
  }

  /* ------------------------------------------------------------ página del carrito */
  function initCart() {
    var root = $('#cart-root');
    if (!root) return;
    function render() {
      var cart = getCart();
      if (!cart.length) {
        root.innerHTML = '<div class="card center" style="grid-column:1/-1"><p>Tu carrito está vacío.</p><a class="btn btn-yellow" href="' + url('/menu/') + '">' + icon('cart') + ' Ver el menú</a></div>';
        return;
      }
      var t = totals(cart);
      var nac = CAT.shipping.filter(function (s) { return s.free_from; })[0];
      var missing = nac ? nac.free_from - t.subtotal : 0;
      root.innerHTML =
        '<div class="card">' + cart.map(function (i) {
          var p = P[i.slug], max = available(i.slug);
          return '<div class="cart-item" data-line="' + i.slug + '">' +
            '<a href="' + url('/producto/' + p.slug + '/') + '"><img src="' + img(p.image) + '" alt="' + esc(p.name) + '" title="' + esc(p.name) + '" width="120" height="58" loading="lazy"></a>' +
            '<div><h2><a href="' + url('/producto/' + p.slug + '/') + '">' + esc(p.name) + '</a></h2>' +
            '<p class="small">' + fmt(p.price) + ' c/u' + (max < 10 ? ' · quedan ' + max : '') + '</p>' +
            '<div class="ci-actions"><div class="qty sm" data-qty><button type="button" data-qty-step="-1" aria-label="Disminuir">' + icon('minus') + '</button>' +
            '<input type="number" min="1" max="' + max + '" value="' + i.qty + '" data-qty-input aria-label="Cantidad de ' + esc(p.name) + '">' +
            '<button type="button" data-qty-step="1" aria-label="Aumentar">' + icon('plus') + '</button></div>' +
            '<button class="icon-btn" data-remove="' + p.slug + '" aria-label="Eliminar ' + esc(p.name) + '">' + icon('trash') + '</button></div></div>' +
            '<p class="ci-total">' + fmt(p.price * i.qty) + '</p></div>';
        }).join('') + '</div>' +
        '<aside class="card summary"><h2>Resumen</h2>' +
        '<div class="summary-row"><span>Productos (' + t.count + ')</span><span>' + fmt(t.subtotal) + '</span></div>' +
        '<div class="summary-row"><span>Envío</span><span>Se calcula al pagar</span></div>' +
        (missing > 0 ? '<p class="progress-free">' + icon('truck') + ' Te faltan <strong>' + fmt(missing) + '</strong> para el envío nacional gratis.</p>' : '<p class="progress-free">' + icon('check') + ' ¡Tienes envío nacional gratis!</p>') +
        '<div class="summary-row total"><span>Subtotal</span><span>' + fmt(t.subtotal) + '</span></div>' +
        '<a class="btn btn-yellow btn-lg" href="' + url('/pagar/') + '">Continuar al pago</a>' +
        '<a class="btn btn-whatsapp" href="' + waLink(cart) + '" target="_blank" rel="noopener" data-track="whatsapp_order">' + icon('whatsapp') + ' Pedir por WhatsApp</a>' +
        '<a class="btn btn-ghost" href="' + url('/menu/') + '">Seguir comprando</a></aside>';
    }
    root.addEventListener('change', function (e) {
      if (!e.target.matches('[data-qty-input]')) return;
      var slug = e.target.closest('[data-line]').getAttribute('data-line');
      var cart = getCart();
      var max = available(slug);
      var v = Math.max(1, Math.min(max, parseInt(e.target.value, 10) || 1));
      if ((parseInt(e.target.value, 10) || 1) > max) toast('Solo hay ' + max + ' disponibles.');
      cart.forEach(function (i) { if (i.slug === slug) i.qty = v; });
      setCart(cart);
      render();
    });
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-remove]');
      if (!b) return;
      var slug = b.getAttribute('data-remove');
      var line = getCart().filter(function (i) { return i.slug === slug; })[0];
      setCart(getCart().filter(function (i) { return i.slug !== slug; }));
      if (line) track('remove_from_cart', { currency: 'MXN', value: P[slug].price * line.qty, items: [gaItem(slug, line.qty)] });
      render();
    });
    render();
    var cart = getCart();
    track('view_cart', { currency: 'MXN', value: totals(cart).subtotal, items: cart.map(function (i) { return gaItem(i.slug, i.qty); }) });
  }

  function waLink(cart, order) {
    var lines = cart.map(function (i) { return '• ' + i.qty + ' x ' + P[i.slug].name + ' (' + fmt(P[i.slug].price * i.qty) + ')'; });
    var text = 'Hola Eke, quiero hacer este pedido' + (order ? ' (folio ' + order.id + ')' : '') + ':\n' + lines.join('\n') + '\nTotal: ' + fmt(order ? order.total : totals(cart).subtotal);
    return 'https://wa.me/' + CAT.whatsapp + '?text=' + encodeURIComponent(text);
  }

  /* ------------------------------------------------------------ envío de formularios (opcional: Formspree) */
  function sendForm(subject, data) {
    if (!CAT.formspree) return Promise.resolve(false);
    var payload = Object.assign({ _subject: subject }, data);
    return fetch('https://formspree.io/f/' + encodeURIComponent(CAT.formspree), {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload)
    }).then(function (r) { return r.ok; }).catch(function () { return false; });
  }

  /* ------------------------------------------------------------ checkout */
  var PAYMENTS = [
    { id: 'mercadopago', label: 'Tarjeta de crédito o débito', help: 'Procesado por Mercado Pago (modo de prueba).' },
    { id: 'paypal', label: 'PayPal', help: 'Paga con tu cuenta PayPal (sandbox).' },
    { id: 'spei', label: 'Transferencia SPEI', help: 'Recibirás los datos bancarios al confirmar.' },
    { id: 'efectivo', label: 'Efectivo al recibir', help: 'Solo para recoger en tienda o entrega en Huejutla.' }
  ];

  function initCheckout() {
    var root = $('#checkout-root');
    if (!root) return;
    var cart = getCart();
    if (!cart.length) {
      root.innerHTML = '<div class="card center" style="grid-column:1/-1"><p>No hay productos en tu carrito.</p><a class="btn btn-yellow" href="' + url('/menu/') + '">Ver el menú</a></div>';
      return;
    }
    var s = store.get('session', {}) || {};
    var last = store.get('last_customer', {}) || {};
    function v(k) { return esc(last[k] || s[k] || ''); }
    root.innerHTML =
      '<form class="card" id="checkout-form" novalidate>' +
      '<h2 class="h3">1. Datos de contacto</h2><div class="form-grid">' +
      '<label>Nombre completo<input name="name" required autocomplete="name" value="' + v('name') + '"></label>' +
      '<label>Correo electrónico<input name="email" type="email" required autocomplete="email" value="' + v('email') + '"></label>' +
      '<label>Teléfono / WhatsApp<input name="phone" type="tel" required pattern="[0-9 +()-]{10,}" autocomplete="tel" value="' + v('phone') + '"></label></div>' +
      '<h2 class="h3">2. Entrega</h2><fieldset class="seg" id="ship-options"><legend class="sr-only">Modalidad de entrega</legend>' +
      CAT.shipping.map(function (o, k) {
        return '<label><input type="radio" name="shipping" value="' + o.id + '"' + (k === 0 ? ' checked' : '') + '><span><strong>' + esc(o.label) + '</strong><small>' +
          (o.cost === 0 ? 'Sin costo' : fmt(o.cost)) + (o.free_from ? ' · gratis desde ' + fmt(o.free_from) : '') + '</small></span></label>';
      }).join('') + '</fieldset>' +
      '<div class="form-grid" id="address-fields">' +
      '<label class="full">Calle y número<input name="address" autocomplete="street-address" value="' + v('address') + '"></label>' +
      '<label>Colonia / localidad<input name="colonia" value="' + v('colonia') + '"></label>' +
      '<label>Código postal<input name="cp" inputmode="numeric" pattern="[0-9]{5}" autocomplete="postal-code" value="' + v('cp') + '"></label>' +
      '<label>Ciudad<input name="city" autocomplete="address-level2" value="' + v('city') + '"></label>' +
      '<label>Estado<input name="state" autocomplete="address-level1" value="' + v('state') + '"></label></div>' +
      '<label>Notas para tu pedido (opcional)<textarea name="notes" rows="2" placeholder="Sin cebolla, referencias del domicilio…"></textarea></label>' +
      '<h2 class="h3" style="margin-top:18px">3. Forma de pago</h2><fieldset class="seg pay-options"><legend class="sr-only">Forma de pago</legend>' +
      PAYMENTS.map(function (p, k) {
        return '<label data-pay="' + p.id + '"><input type="radio" name="payment" value="' + p.id + '"' + (k === 0 ? ' checked' : '') + '><span><strong>' + p.label + '</strong><small>' + p.help + '</small></span></label>';
      }).join('') + '</fieldset>' +
      '<label style="display:flex;gap:8px;align-items:flex-start;font-weight:400;margin-top:12px"><input type="checkbox" name="privacy" required> <span>Acepto el <a href="' + url('/aviso-de-privacidad/') + '" target="_blank">aviso de privacidad</a>.</span></label>' +
      '<p class="form-msg" data-form-msg role="alert"></p>' +
      '</form>' +
      '<aside class="card summary" id="checkout-summary"></aside>';

    var form = $('#checkout-form');
    function current() { return form.querySelector('input[name=shipping]:checked').value; }
    function update() {
      var shipId = current();
      var nacional = shipId === 'nacional', recoger = shipId === 'recoger';
      $('#address-fields').hidden = recoger;
      $$('#address-fields input').forEach(function (i) { i.required = !recoger && i.name !== 'colonia'; });
      var cash = $('[data-pay="efectivo"]');
      cash.hidden = nacional;
      if (nacional && cash.querySelector('input').checked) form.querySelector('input[name=payment][value=mercadopago]').checked = true;
      var t = totals(cart, shipId);
      $('#checkout-summary').innerHTML = '<h2>Tu pedido</h2>' +
        cart.map(function (i) { return '<div class="mini-item"><span>' + i.qty + ' × ' + esc(P[i.slug].name) + '</span><span>' + fmt(P[i.slug].price * i.qty) + '</span></div>'; }).join('') +
        '<div class="summary-row" style="margin-top:12px"><span>Subtotal</span><span>' + fmt(t.subtotal) + '</span></div>' +
        '<div class="summary-row"><span>Envío</span><span>' + (t.ship.cost === 0 ? 'Gratis' : fmt(t.ship.cost)) + '</span></div>' +
        '<div class="summary-row total"><span>Total</span><span>' + fmt(t.total) + '</span></div>' +
        '<button class="btn btn-yellow btn-lg" type="submit" form="checkout-form" id="pay-btn">' + icon('shield') + ' Pagar ' + fmt(t.total) + '</button>' +
        '<p class="small center" style="margin-top:8px">' + icon('shield') + ' Pago protegido · Modo de prueba</p>';
    }
    form.addEventListener('change', function (e) {
      if (e.target.name === 'shipping') { update(); track('add_shipping_info', { currency: 'MXN', value: totals(cart).subtotal, shipping_tier: e.target.value }); }
      if (e.target.name === 'payment') track('add_payment_info', { currency: 'MXN', value: totals(cart).subtotal, payment_type: e.target.value });
    });
    update();
    track('begin_checkout', { currency: 'MXN', value: totals(cart).subtotal, items: cart.map(function (i) { return gaItem(i.slug, i.qty); }) });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = $('[data-form-msg]', form);
      if (!form.checkValidity()) {
        msg.className = 'form-msg err';
        msg.textContent = 'Revisa los campos marcados: faltan datos o tienen un formato incorrecto.';
        form.reportValidity();
        return;
      }
      // Verificar inventario al momento de pagar
      var problem = cart.filter(function (i) { return i.qty > available(i.slug); })[0];
      if (problem) { msg.className = 'form-msg err'; msg.textContent = 'Ya no hay suficiente existencia de ' + P[problem.slug].name + '. Ajusta tu carrito.'; return; }

      var fd = new FormData(form);
      var data = {};
      fd.forEach(function (val, key) { data[key] = String(val).trim(); });
      var t = totals(cart, data.shipping);
      var order = {
        id: 'EKE-' + today() + '-' + rand(4),
        date: new Date().toISOString(),
        items: cart.map(function (i) { return { slug: i.slug, name: P[i.slug].name, price: P[i.slug].price, qty: i.qty }; }),
        subtotal: t.subtotal, shipping: t.ship, total: t.total,
        payment: data.payment, status: 0,
        customer: { name: data.name, email: data.email, phone: data.phone, address: data.address, colonia: data.colonia, cp: data.cp, city: data.city, state: data.state, notes: data.notes }
      };
      var btn = $('#pay-btn');
      btn.disabled = true;
      btn.textContent = 'Procesando pago de prueba…';
      setTimeout(function () {
        var s2 = sold();
        cart.forEach(function (i) { s2[i.slug] = (s2[i.slug] || 0) + i.qty; });
        store.set('sold', s2);
        var orders = store.get('orders', []);
        orders.unshift(order);
        store.set('orders', orders);
        store.set('last_customer', order.customer);
        setCart([]);
        track('purchase', { transaction_id: order.id, currency: 'MXN', value: order.total, shipping: order.shipping.cost, payment_type: order.payment, items: order.items.map(function (i) { return gaItem(i.slug, i.qty); }) });
        sendForm('Nuevo pedido ' + order.id, { pedido: order.id, total: fmt(order.total), cliente: order.customer, productos: order.items, entrega: order.shipping.label, pago: order.payment }).then(function () {
          location.href = url('/pedido-confirmado/') + '?id=' + encodeURIComponent(order.id);
        });
      }, 1200);
    });
  }

  /* ------------------------------------------------------------ confirmación y seguimiento */
  var ORDER_STEPS = ['Recibido', 'En preparación', 'En camino', 'Entregado'];
  var TICKET_STEPS = ['Registrado', 'Clasificado', 'En atención', 'Resuelto', 'Cerrado'];
  function timeline(steps, idx) {
    return '<ol class="timeline">' + steps.map(function (s, k) { return '<li class="' + (k <= idx ? 'done' : '') + '">' + s + '</li>'; }).join('') + '</ol>';
  }
  function findOrder(id) { return store.get('orders', []).filter(function (o) { return o.id.toUpperCase() === id.toUpperCase(); })[0]; }
  function findTicket(id) { return store.get('tickets', []).filter(function (o) { return o.id.toUpperCase() === id.toUpperCase(); })[0]; }
  function payLabel(id) { var p = PAYMENTS.filter(function (x) { return x.id === id; })[0]; return p ? p.label : id; }

  function orderSummary(o) {
    return '<div class="card track-result" style="text-align:left">' +
      '<p><strong>Folio:</strong> ' + esc(o.id) + ' · ' + dateStr(o.date) + '</p>' +
      timeline(ORDER_STEPS, o.status) +
      o.items.map(function (i) { return '<div class="mini-item"><span>' + i.qty + ' × ' + esc(i.name) + '</span><span>' + fmt(i.price * i.qty) + '</span></div>'; }).join('') +
      '<div class="summary-row"><span>Envío (' + esc(o.shipping.label) + ')</span><span>' + (o.shipping.cost ? fmt(o.shipping.cost) : 'Gratis') + '</span></div>' +
      '<div class="summary-row total"><span>Total</span><span>' + fmt(o.total) + '</span></div>' +
      '<p class="small">Forma de pago: ' + esc(payLabel(o.payment)) + '</p></div>';
  }

  function initConfirm() {
    var root = $('#confirm-root');
    if (!root) return;
    var o = findOrder(params().get('id') || '');
    if (!o) { root.innerHTML = '<h1 class="section-title">Pedido no encontrado</h1><p>No encontramos ese pedido en este dispositivo.</p><a class="btn btn-yellow" href="' + url('/seguimiento/') + '">Ir a seguimiento</a>'; return; }
    var extra = '';
    if (o.payment === 'spei') extra = '<p class="notice">' + icon('mail') + '<span>Realiza tu transferencia SPEI por <strong>' + fmt(o.total) + '</strong> con el concepto <strong>' + esc(o.id) + '</strong>. Datos bancarios de ejemplo: CLABE 000 000 0000000000 00 (configura la real antes de publicar).</span></p>';
    if (o.payment === 'efectivo') extra = '<p class="notice">' + icon('check') + '<span>Pagarás <strong>' + fmt(o.total) + '</strong> en efectivo al recibir tu pedido.</span></p>';
    root.innerHTML = '<h1 class="section-title">¡Gracias por tu pedido, ' + esc(o.customer.name.split(' ')[0]) + '!</h1>' +
      '<p>Tu número de pedido es</p><p class="folio">' + esc(o.id) + '</p>' +
      '<p>Guárdalo para consultar el estado en <a href="' + url('/seguimiento/') + '?folio=' + encodeURIComponent(o.id) + '">Seguimiento de pedido</a>.</p>' +
      extra + orderSummary(o) +
      '<p><a class="btn btn-whatsapp" href="' + waLink(o.items.map(function (i) { return { slug: i.slug, qty: i.qty }; }).filter(function (i) { return P[i.slug]; }), o) + '" target="_blank" rel="noopener">' + icon('whatsapp') + ' Confirmar por WhatsApp</a> ' +
      '<a class="btn btn-ghost" href="' + url('/menu/') + '">Seguir comprando</a></p>';
  }

  function ticketSummary(t) {
    return '<div class="card track-result">' +
      '<p><strong>Ticket:</strong> ' + esc(t.id) + ' · ' + dateStr(t.date) + ' · <span class="pill ' + t.prioridad.toLowerCase() + '">' + t.prioridad + ' ' + t.prioridadNombre + '</span></p>' +
      timeline(TICKET_STEPS, t.estado) +
      '<p><strong>' + esc(t.asunto) + '</strong> (' + esc(t.tipo) + ' · ' + esc(t.categoria) + ')</p>' +
      '<p class="small">Primera respuesta en ' + t.sla.respuesta + ' · resolución objetivo en ' + t.sla.resolucion + ' (horario de atención).</p></div>';
  }

  function initTrack() {
    var form = $('[data-track-form]');
    if (!form) return;
    var out = $('#track-root');
    function lookup(id) {
      id = id.trim();
      var o = findOrder(id), t = findTicket(id);
      if (o) out.innerHTML = orderSummary(o);
      else if (t) out.innerHTML = ticketSummary(t);
      else out.innerHTML = '<p class="notice">' + icon('help') + '<span>No encontramos el folio <strong>' + esc(id) + '</strong> en este dispositivo. Si hiciste tu pedido desde otro equipo, <a href="' + url('/ayuda/') + '">abre un ticket</a> o escríbenos por WhatsApp.</span></p>';
      track('order_tracking', { found: !!(o || t) });
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); lookup(form.folio.value); });
    var f = params().get('folio');
    if (f) { form.folio.value = f; lookup(f); }
    var orders = store.get('orders', []), tickets = store.get('tickets', []);
    if (orders.length || tickets.length) {
      $('#history-root').innerHTML = '<h2 class="h3">Tus folios en este dispositivo</h2><ul>' +
        orders.map(function (o) { return '<li><a href="?folio=' + encodeURIComponent(o.id) + '">' + esc(o.id) + '</a> · pedido · ' + fmt(o.total) + '</li>'; }).join('') +
        tickets.map(function (t) { return '<li><a href="?folio=' + encodeURIComponent(t.id) + '">' + esc(t.id) + '</a> · ticket · ' + esc(t.asunto) + '</li>'; }).join('') + '</ul>';
    }
  }

  /* ------------------------------------------------------------ mesa de ayuda (ITIL) */
  var PRIORITY = {
    'alto-alta': 'P1', 'alto-media': 'P2', 'alto-baja': 'P3',
    'medio-alta': 'P2', 'medio-media': 'P3', 'medio-baja': 'P4',
    'bajo-alta': 'P3', 'bajo-media': 'P4', 'bajo-baja': 'P4'
  };
  var SLA = {
    P1: { nombre: 'Crítica', respuesta: '1 h', resolucion: '4 h' },
    P2: { nombre: 'Alta', respuesta: '2 h', resolucion: '8 h' },
    P3: { nombre: 'Media', respuesta: '4 h', resolucion: '24 h' },
    P4: { nombre: 'Baja', respuesta: '8 h', resolucion: '48 h' }
  };
  function initTicketForm() {
    var form = $('#ticket-form');
    if (!form) return;
    var out = $('[data-priority-out]', form);
    function prio() { return PRIORITY[form.impacto.value + '-' + form.urgencia.value]; }
    function show() {
      var p = prio(), s = SLA[p];
      out.innerHTML = 'Prioridad calculada: <span class="pill ' + p.toLowerCase() + '">' + p + ' ' + s.nombre + '</span> · primera respuesta en ' + s.respuesta + ', resolución en ' + s.resolucion + '.';
    }
    $$('[data-priority-input]', form).forEach(function (el) { el.addEventListener('change', show); });
    show();
    var sess = store.get('session', null);
    if (sess) { form.nombre.value = sess.name; form.email.value = sess.email; }
    var pre = params().get('pedido');
    if (pre) form.pedido.value = pre;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = $('[data-form-msg]', form);
      if (!form.checkValidity()) { msg.className = 'form-msg err'; msg.textContent = 'Completa los campos obligatorios.'; form.reportValidity(); return; }
      var p = prio();
      var t = {
        id: 'TCK-' + rand(5), date: new Date().toISOString(),
        tipo: form.tipo.value, categoria: form.categoria.value, impacto: form.impacto.value, urgencia: form.urgencia.value,
        prioridad: p, prioridadNombre: SLA[p].nombre, sla: SLA[p],
        nombre: form.nombre.value.trim(), email: form.email.value.trim(), pedido: form.pedido.value.trim(),
        asunto: form.asunto.value.trim(), descripcion: form.descripcion.value.trim(), estado: 1
      };
      var list = store.get('tickets', []);
      list.unshift(t);
      store.set('tickets', list);
      track('generate_lead', { method: 'helpdesk', ticket_type: t.tipo, ticket_category: t.categoria, priority: p });
      sendForm('[' + p + '] ' + t.tipo + ': ' + t.asunto + ' (' + t.id + ')', t).then(function (sent) {
        msg.className = 'form-msg ok';
        msg.innerHTML = icon('check') + ' Ticket registrado con folio <strong>' + t.id + '</strong> (prioridad ' + p + '). ' +
          (sent ? 'Te enviamos la confirmación por correo. ' : '') +
          '<a href="' + url('/seguimiento/') + '?folio=' + t.id + '">Consultar estado</a>';
        form.asunto.value = ''; form.descripcion.value = '';
      });
    });
  }

  /* ------------------------------------------------------------ cuenta (demostración local) */
  function sha256(text) {
    if (!(window.crypto && crypto.subtle)) return Promise.resolve(btoa(unescape(encodeURIComponent(text))));
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    });
  }
  function initAccount() {
    var root = $('#account-root');
    if (!root) return;
    function render() {
      var s = store.get('session', null);
      if (s) {
        var orders = store.get('orders', []).filter(function (o) { return o.customer.email === s.email; });
        var tickets = store.get('tickets', []).filter(function (t) { return t.email === s.email; });
        root.innerHTML = '<h1 class="section-title">Hola, ' + esc(s.name) + '</h1>' +
          '<div class="card"><h2 class="h3">Mis pedidos</h2>' + (orders.length ? '<ul>' + orders.map(function (o) { return '<li><a href="' + url('/seguimiento/') + '?folio=' + o.id + '">' + o.id + '</a> · ' + dateStr(o.date) + ' · ' + fmt(o.total) + '</li>'; }).join('') + '</ul>' : '<p>Aún no tienes pedidos.</p>') +
          '<h2 class="h3">Mis tickets de soporte</h2>' + (tickets.length ? '<ul>' + tickets.map(function (t) { return '<li><a href="' + url('/seguimiento/') + '?folio=' + t.id + '">' + t.id + '</a> · ' + esc(t.asunto) + '</li>'; }).join('') + '</ul>' : '<p>No tienes tickets abiertos.</p>') +
          '<p><a class="btn btn-ghost" href="' + url('/favoritos/') + '">' + icon('heart') + ' Mis favoritos</a> <button class="btn btn-wine" data-logout>Cerrar sesión</button></p></div>';
        return;
      }
      root.innerHTML = '<h1 class="section-title">Mi cuenta</h1>' +
        '<div class="card"><div class="account-tabs" role="tablist"><button class="btn btn-ghost" role="tab" aria-selected="true" data-tab="login">Iniciar sesión</button><button class="btn btn-ghost" role="tab" aria-selected="false" data-tab="register">Crear cuenta</button></div>' +
        '<form id="account-form" data-mode="login"><div class="form-grid">' +
        '<label class="full" data-only="register" hidden>Nombre completo<input name="name" autocomplete="name"></label>' +
        '<label class="full">Correo electrónico<input name="email" type="email" required autocomplete="email"></label>' +
        '<label class="full">Contraseña<input name="password" type="password" required minlength="6" autocomplete="current-password"></label></div>' +
        '<button class="btn btn-wine btn-lg" type="submit">Entrar</button><p class="form-msg" data-form-msg role="alert"></p>' +
        '<p class="small">Demostración: la cuenta se guarda solo en este navegador (contraseña cifrada con SHA-256).</p></form></div>';
    }
    root.addEventListener('click', function (e) {
      var tab = e.target.closest('[data-tab]');
      if (tab) {
        var mode = tab.getAttribute('data-tab'), form = $('#account-form');
        form.setAttribute('data-mode', mode);
        $$('[data-tab]', root).forEach(function (b) { b.setAttribute('aria-selected', b === tab ? 'true' : 'false'); });
        $$('[data-only="register"]', form).forEach(function (el) { el.hidden = mode !== 'register'; el.querySelector('input').required = mode === 'register'; });
        $('button[type=submit]', form).textContent = mode === 'register' ? 'Crear cuenta' : 'Entrar';
      }
      if (e.target.closest('[data-logout]')) { store.set('session', null); location.reload(); }
    });
    root.addEventListener('submit', function (e) {
      e.preventDefault();
      var form = e.target, msg = $('[data-form-msg]', form);
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var mode = form.getAttribute('data-mode');
      var email = form.email.value.trim().toLowerCase();
      sha256(email + ':' + form.password.value).then(function (hash) {
        var users = store.get('users', {});
        if (mode === 'register') {
          if (users[email]) { msg.className = 'form-msg err'; msg.textContent = 'Ya existe una cuenta con ese correo.'; return; }
          users[email] = { name: form.name.value.trim(), email: email, hash: hash };
          store.set('users', users);
          track('sign_up', { method: 'email' });
        } else if (!users[email] || users[email].hash !== hash) {
          msg.className = 'form-msg err'; msg.textContent = 'Correo o contraseña incorrectos.'; return;
        } else {
          track('login', { method: 'email' });
        }
        store.set('session', { name: users[email].name, email: email });
        renderHeader();
        render();
      });
    });
    render();
  }

  /* ------------------------------------------------------------ favoritos (página) */
  function initFavPage() {
    var root = $('#fav-root');
    if (!root) return;
    var f = favs().filter(function (s) { return P[s]; });
    if (!f.length) { root.innerHTML = '<div class="card center"><p>Aún no tienes favoritos. Toca el corazón de un producto para guardarlo.</p><a class="btn btn-yellow" href="' + url('/menu/') + '">Ver el menú</a></div>'; return; }
    root.innerHTML = '<div class="grid products">' + f.map(function (s) {
      var p = P[s];
      return '<article class="card product" data-product="' + s + '"><a class="card-media" href="' + url('/producto/' + s + '/') + '"><img src="' + img(p.image) + '" alt="' + esc(p.name) + '" title="' + esc(p.name) + '" width="263" height="126" loading="lazy"></a>' +
        '<button class="fav" data-fav="' + s + '" aria-pressed="true" aria-label="Quitar de favoritos">' + icon('heart') + '</button>' +
        '<div class="card-body"><h2 class="card-title"><a href="' + url('/producto/' + s + '/') + '">' + esc(p.name) + '</a></h2><p class="card-desc">' + esc(p.short) + '</p><p class="stock" data-stock-for="' + s + '"></p><p class="price">' + fmt(p.price) + '</p>' +
        '<button class="btn btn-wine" data-add-to-cart="' + s + '">' + icon('cart') + ' Agregar al carrito</button></div></article>';
    }).join('') + '</div>';
  }

  /* ------------------------------------------------------------ boletín (email marketing) */
  function initNewsletter() {
    $$('[data-newsletter]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var email = form.email.value.trim();
        var list = store.get('newsletter', []);
        if (list.indexOf(email) < 0) list.push(email);
        store.set('newsletter', list);
        track('generate_lead', { method: 'newsletter' });
        sendForm('Nueva suscripción al boletín', { email: email }).then(function () {
          form.innerHTML = '<p>' + icon('check') + ' ¡Listo! Te suscribiste con <strong>' + esc(email) + '</strong>.</p>';
        });
      });
    });
  }

  /* ------------------------------------------------------------ métricas de rendimiento (Web Vitals) */
  var vitals = {};
  function initVitals() {
    try {
      new PerformanceObserver(function (l) { var e = l.getEntries(); vitals.lcp = Math.round(e[e.length - 1].startTime); }).observe({ type: 'largest-contentful-paint', buffered: true });
      vitals.cls = 0;
      new PerformanceObserver(function (l) { l.getEntries().forEach(function (e) { if (!e.hadRecentInput) vitals.cls += e.value; }); }).observe({ type: 'layout-shift', buffered: true });
      new PerformanceObserver(function (l) { l.getEntries().forEach(function (e) { if (e.name === 'first-contentful-paint') vitals.fcp = Math.round(e.startTime); }); }).observe({ type: 'paint', buffered: true });
    } catch (e) { /* navegador sin soporte */ }
    window.addEventListener('load', function () {
      setTimeout(function () {
        var nav = performance.getEntriesByType('navigation')[0];
        if (nav) { vitals.ttfb = Math.round(nav.responseStart); vitals.load = Math.round(nav.loadEventEnd || nav.duration); }
      }, 0);
    });
    var sent = false;
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState !== 'hidden' || sent) return;
      sent = true;
      track('web_vitals', { lcp: vitals.lcp, cls: vitals.cls != null ? Number(vitals.cls.toFixed(3)) : undefined, fcp: vitals.fcp, ttfb: vitals.ttfb, page_load: vitals.load, page_path: location.pathname });
    });
    window.addEventListener('error', function (e) { track('exception', { description: String(e.message).slice(0, 150), fatal: false }); });
  }

  /* ------------------------------------------------------------ página de estado */
  function initStatus() {
    var live = $('#status-live');
    if (!live) return;
    var targets = [['Página de inicio', '/'], ['Menú', '/menu/'], ['Catálogo (JS)', '/assets/js/catalog.js'], ['sitemap.xml', '/sitemap.xml'], ['robots.txt', '/robots.txt']];
    Promise.all(targets.map(function (t) {
      var t0 = performance.now();
      return fetch(url(t[1]), { cache: 'no-store' }).then(function (r) { return [t[0], r.status, Math.round(performance.now() - t0)]; })
        .catch(function () { return [t[0], 'Error', '–']; });
    })).then(function (rows) {
      live.tBodies[0].innerHTML = rows.map(function (r) {
        var ok = r[1] >= 200 && r[1] < 400;
        return '<tr><td>' + r[0] + '</td><td class="' + (ok ? 'ok-text' : 'bad-text') + '">' + r[1] + '</td><td>' + r[2] + (r[2] !== '–' ? ' ms' : '') + '</td></tr>';
      }).join('');
    });

    setTimeout(function () {
      var rows = [['LCP (Largest Contentful Paint)', vitals.lcp, 'ms', '≤ 2500 ms', 2500], ['FCP (First Contentful Paint)', vitals.fcp, 'ms', '≤ 1800 ms', 1800], ['TTFB (Time to First Byte)', vitals.ttfb, 'ms', '≤ 800 ms', 800], ['CLS (Cumulative Layout Shift)', vitals.cls != null ? vitals.cls.toFixed(3) : null, '', '≤ 0.1', 0.1], ['Carga completa', vitals.load, 'ms', '≤ 3000 ms', 3000]];
      $('#status-vitals').tBodies[0].innerHTML = rows.map(function (r) {
        var has = r[1] != null;
        return '<tr><td>' + r[0] + '</td><td class="' + (has ? (Number(r[1]) <= r[4] ? 'ok-text' : 'bad-text') : '') + '">' + (has ? r[1] + ' ' + r[2] : 'No disponible') + '</td><td>' + r[3] + '</td></tr>';
      }).join('');
    }, 2500);

    fetch(url('/assets/data/metrics.csv'), { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(); return r.text(); }).then(function (csv) {
      var lines = csv.trim().split(/\r?\n/).slice(1).map(function (l) { return l.split(','); }).filter(function (c) { return c.length >= 5; });
      if (!lines.length) return;
      var ok = lines.filter(function (c) { return c[4] === '1'; }).length;
      var errs = lines.filter(function (c) { return !(+c[2] >= 200 && +c[2] < 400); }).length;
      var times = lines.map(function (c) { return +c[3]; }).filter(function (n) { return n > 0; });
      var avg = times.length ? Math.round(times.reduce(function (a, b) { return a + b; }, 0) / times.length) : 0;
      $('[data-stat="uptime"]').textContent = (ok * 100 / lines.length).toFixed(2) + ' %';
      $('[data-stat-note="uptime"]').textContent = lines.length + ' comprobaciones registradas (objetivo ≥ 99.5 %)';
      $('[data-stat="avg"]').textContent = avg + ' ms';
      $('[data-stat="errors"]').textContent = (errs * 100 / lines.length).toFixed(2) + ' %';
      $('#status-history').innerHTML = '<thead><tr><th scope="col">Fecha (UTC)</th><th scope="col">URL</th><th scope="col">HTTP</th><th scope="col">Tiempo</th></tr></thead><tbody>' +
        lines.slice(-25).reverse().map(function (c) { return '<tr><td>' + esc(c[0]) + '</td><td>' + esc(c[1]) + '</td><td class="' + (c[4] === '1' ? 'ok-text' : 'bad-text') + '">' + esc(c[2]) + '</td><td>' + esc(c[3]) + ' ms</td></tr>'; }).join('') + '</tbody>';
    }).catch(function () { /* sin historial todavía */ });
  }

  /* ------------------------------------------------------------ arranque */
  function init() {
    renderHeader();
    initVitals();
    initCarousel();
    initCatalog();
    initProductPage();
    initCart();
    initCheckout();
    initConfirm();
    initTrack();
    initTicketForm();
    initAccount();
    initFavPage();
    initNewsletter();
    initStatus();
    renderStock();
    renderFavs();
    $$('video[data-video-title]').forEach(function (v) {
      var started = false;
      v.addEventListener('play', function () { if (!started) { started = true; track('video_start', { video_title: v.getAttribute('data-video-title'), video_provider: 'self-hosted' }); } });
      v.addEventListener('ended', function () { track('video_complete', { video_title: v.getAttribute('data-video-title'), video_provider: 'self-hosted' }); });
    });
    var shareNative = $$('.share-native');
    if (navigator.share) shareNative.forEach(function (b) { b.hidden = false; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
