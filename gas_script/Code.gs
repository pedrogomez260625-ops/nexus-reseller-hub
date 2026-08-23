// ============================================================================
// NEXUS RESELLER CORE - GOOGLE APPS SCRIPT SERVERLESS INTERACTIVE BOT & DB
// Replicación completa de Bunny Tools con Menús Inline, Categorías y Entrega 1-Seg
// ============================================================================

var BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN";
var BUNNY_API_KEY = "YOUR_BUNNY_API_KEY";
var ADMIN_ID = 1849945160; // @Cctes001
var TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN;

// 💳 Billeteras de Depósito para Clientes
var DEPOSIT_WALLET_BSC = "0xec0183f1411c106afb8cfe32c391fef536f681d4"; // USDT BEP20
var DEPOSIT_WALLET_TRON = "TKuRmAYaCQR3nTv3M8XtRZ8VwXfuLHWPbE"; // USDT TRC20

// 📦 Catálogo de Productos y Precios (Costo Mayorista vs. Tu Precio de Venta)
var CATALOG = {
  "cat_ai": {
    "name": "🤖 Modelos de IA",
    "desc": "Herramientas líderes de Inteligencia Artificial",
    "products": {
      "gemini_pro_18m": { "name": "Google Gemini Pro (18 Meses)", "price": 4.00, "supplier_id": 101, "desc": "Acceso Gemini 1.5/2.0 con 2M tokens context." },
      "claude_sonnet": { "name": "Claude 3.5 Sonnet Pro (1 Mes)", "price": 4.50, "supplier_id": 102, "desc": "Claude Pro con Artifacts y Projects." },
      "chatgpt_plus": { "name": "ChatGPT Plus (1 Mes)", "price": 3.80, "supplier_id": 103, "desc": "Acceso a GPT-4o y Canvas sin límites." },
      "perplexity_pro": { "name": "Perplexity Pro AI (1 Año)", "price": 5.50, "supplier_id": 104, "desc": "Búsquedas ilimitadas con GPT-4o y Claude." }
    }
  },
  "cat_dev": {
    "name": "💻 Programación & Dev",
    "desc": "IDEs y asistentes de código",
    "products": {
      "cursor_ai": { "name": "Cursor AI Pro (1 Mes)", "price": 4.50, "supplier_id": 201, "desc": "Editor de código VS Code con IA nativa." },
      "github_copilot": { "name": "GitHub Copilot (1 Año)", "price": 6.00, "supplier_id": 202, "desc": "Autocompletado y chat en IDEs." },
      "jetbrains_all": { "name": "JetBrains All Products (1 Año)", "price": 7.00, "supplier_id": 203, "desc": "PyCharm, IntelliJ, DataGrip y más." }
    }
  },
  "cat_design": {
    "name": "🎨 Diseño & Gráficos",
    "desc": "Plataformas de diseño y generación gráfica",
    "products": {
      "canva_pro": { "name": "Canva Pro (1 Año)", "price": 2.80, "supplier_id": 301, "desc": "Plantillas, Magic Studio y Brand Kit." },
      "midjourney": { "name": "Midjourney Standard (1 Mes)", "price": 5.00, "supplier_id": 302, "desc": "Generación de imágenes fotorrealistas." }
    }
  },
  "cat_vpn": {
    "name": "🔐 VPN & Seguridad",
    "desc": "Navegación cifrada y anónima",
    "products": {
      "nordvpn": { "name": "NordVPN Premium (1 Año)", "price": 3.50, "supplier_id": 401, "desc": "60 países y servidores ultrarrápidos." },
      "surfshark": { "name": "Surfshark VPN (1 Año)", "price": 3.50, "supplier_id": 402, "desc": "Dispositivos ilimitados y CleanWeb." }
    }
  }
};

// ============================================================================
// 1. RECEPTOR WEBHOOK DE TELEGRAM (doPost)
// ============================================================================

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService.createTextOutput("OK");
    }
    var update = JSON.parse(e.postData.contents);
    
    // 🛡️ Blindaje Anti-Duplicados: Si Telegram reenvía el mismo update, se descarta al instante
    if (update.update_id) {
      var cache = CacheService.getScriptCache();
      var cacheKey = "upd_" + update.update_id;
      if (cache.get(cacheKey)) {
        return ContentService.createTextOutput("OK");
      }
      cache.put(cacheKey, "1", 120); // Bloqueo de 2 minutos para duplicados
    }

    if (update.message) {
      handleIncomingMessage(update.message);
    } else if (update.callback_query) {
      handleCallbackQuery(update.callback_query);
    }
  }
  return ContentService.createTextOutput("OK");
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({status: "online", system: "Nexus Core GAS 24/7"})).setMimeType(ContentService.MimeType.JSON);
}

// ============================================================================
// 2. CONTROLADOR DE MENSAJES DE TEXTO
// ============================================================================

function handleIncomingMessage(msg) {
  var chatId = msg.chat.id;
  var userId = msg.from.id;
  var userName = msg.from.first_name || "Cliente";
  var text = (msg.text || "").trim();
  
  var balance = getUserBalance(userId);

  // Comando de Administrador para recargar saldo a un usuario: /dar_saldo <id> <monto>
  if (text.indexOf("/dar_saldo") === 0 && userId === ADMIN_ID) {
    var parts = text.split(" ");
    if (parts.length === 3) {
      var targetId = parts[1];
      var amount = parseFloat(parts[2]);
      var currentBal = getUserBalance(targetId);
      var newBal = currentBal + amount;
      setUserBalance(targetId, newBal);
      sendMessage(chatId, "✅ *Saldo Acreditado:*\nUsuario: `" + targetId + "`\nNuevo Saldo: `$" + newBal.toFixed(2) + " USDT`");
      sendMessage(targetId, "💰 *¡Se ha acreditado tu recarga!*\nHas recibido: `$" + amount.toFixed(2) + " USDT`\nSaldo actual: `$" + newBal.toFixed(2) + " USDT`");
      return;
    } else {
      sendMessage(chatId, "ℹ️ Formato: `/dar_saldo <id_usuario> <monto>`\nEjemplo: `/dar_saldo 1849945160 10.0`");
      return;
    }
  }

  // Comando para panel de control admin: /admin
  if (text === "/admin" && userId === ADMIN_ID) {
    sendMessage(chatId, "👑 *PANEL DE CONTROL ADMIN*\n\n" +
                        "👤 *Tu ID:* `" + userId + "`\n" +
                        "🤖 *Bot:* `@nexus_ai_store_bot`\n\n" +
                        "👉 Para cargar saldo a un cliente o a ti mismo:\n`/dar_saldo <ID_USUARIO> <MONTO>`\n\n" +
                        "Ejemplo:\n`/dar_saldo " + ADMIN_ID + " 10.0`");
    return;
  }

  if (text === "/start" || text === "🛍️ Catálogo") {
    var welcomeText = "⚡ *¡Bienvenido a Nexus Digital Store, " + userName + "!* ⚡\n\n" +
                      "🔥 *Proveedor mayorista de Cuentas Premium y Modelos de IA.*\n" +
                      "🚀 _Entrega 100% automatizada e instantánea en 1 segundo._\n\n" +
                      "💰 *Tu Saldo Disponible:* `$" + balance.toFixed(2) + " USDT`\n\n" +
                      "📂 *Selecciona una categoría para ver productos:*";
    sendInlineKeyboard(chatId, welcomeText, getCategoriesKeyboard());
  }
  else if (text === "/saldo" || text === "💳 Mi Saldo") {
    sendBalanceMenu(chatId, userId, balance);
  }
  else if (text === "/compras" || text === "📦 Mis Compras") {
    sendUserOrders(chatId, userId);
  }
  else {
    sendInlineKeyboard(chatId, "Usa el menú interactivo para explorar el catálogo:", getCategoriesKeyboard());
  }
}

// ============================================================================
// 3. CONTROLADOR DE BOTONES INTERACTIVOS (CALLBACK QUERIES)
// ============================================================================

function handleCallbackQuery(cq) {
  var cqId = cq.id;
  var chatId = cq.message.chat.id;
  var messageId = cq.message.message_id;
  var userId = cq.from.id;
  var data = cq.data;
  var balance = getUserBalance(userId);

  answerCallbackQuery(cqId);

  if (data === "show_categories" || data === "main_menu") {
    editMessageText(chatId, messageId, "📂 *Selecciona una categoría de productos:*", getCategoriesKeyboard());
  }
  else if (data.indexOf("cat_") === 0) {
    var catKey = data;
    var cat = CATALOG[catKey];
    if (cat) {
      var catText = "🏷️ *Categoría:* " + cat.name + "\n" +
                    "📝 _" + cat.desc + "_\n\n" +
                    "Selecciona un producto para ver detalles y precio:";
      editMessageText(chatId, messageId, catText, getProductsKeyboard(catKey));
    }
  }
  else if (data.indexOf("prod_") === 0) {
    var prodKey = data.replace("prod_", "");
    var product = findProduct(prodKey);
    if (product) {
      var pText = "📦 *" + product.name + "*\n\n" +
                  "📝 *Descripción:* " + product.desc + "\n\n" +
                  "💰 *Precio:* `$" + product.price.toFixed(2) + " USDT`\n" +
                  "📊 *Stock:* `Disponible (Entrega Inmediata)`\n\n" +
                  "¿Deseas adquirir esta licencia ahora?";
      var actionKeyboard = [
        [{ text: "⚡ Comprar Ahora ($" + product.price.toFixed(2) + " USDT)", callback_data: "buy_" + prodKey }],
        [{ text: "🔙 Volver a Categorías", callback_data: "show_categories" }]
      ];
      editMessageText(chatId, messageId, pText, actionKeyboard);
    }
  }
  else if (data.indexOf("buy_") === 0) {
    var pKey = data.replace("buy_", "");
    var p = findProduct(pKey);
    if (!p) return;

    if (balance < p.price) {
      var needed = p.price - balance;
      var noBalanceText = "❌ *Saldo Insuficiente*\n\n" +
                          "Producto: *" + p.name + "*\n" +
                          "Precio: `$" + p.price.toFixed(2) + " USDT`\n" +
                          "Tu saldo: `$" + balance.toFixed(2) + " USDT`\n" +
                          "Te faltan: `$" + needed.toFixed(2) + " USDT`\n\n" +
                          "👉 Presiona *Recargar Saldo* para continuar.";
      var rechargeKb = [
        [{ text: "💳 Recargar Saldo USDT", callback_data: "recharge_menu" }],
        [{ text: "🔙 Volver al Producto", callback_data: "prod_" + pKey }]
      ];
      editMessageText(chatId, messageId, noBalanceText, rechargeKb);
      return;
    }

    // Procesar compra automática
    var newBalance = balance - p.price;
    setUserBalance(userId, newBalance);

    // Llamada mayorista a Bunny AI Tools
    var deliveredCredential = callBunnySupplierAPI(p.supplier_id);

    // Registrar compra en memoria
    recordUserOrder(userId, p.name, deliveredCredential, p.price);

    var successText = "🎉 *¡COMPRA COMPLETADA CON ÉXITO!* 🎉\n\n" +
                      "📦 *Producto:* " + p.name + "\n" +
                      "💰 *Total debitado:* `$" + p.price.toFixed(2) + " USDT`\n" +
                      "💳 *Saldo restante:* `$" + newBalance.toFixed(2) + " USDT`\n\n" +
                      "🔑 *TUS CREDENCIALES / LICENCIA:*\n" +
                      "`" + deliveredCredential + "`\n\n" +
                      "🌟 _¡Gracias por confiar en Nexus Digital Store!_";
    var afterBuyKb = [
      [{ text: "🛍️ Seguir Comprando", callback_data: "show_categories" }],
      [{ text: "📦 Ver Mis Compras", callback_data: "view_orders" }]
    ];
    editMessageText(chatId, messageId, successText, afterBuyKb);
  }
  else if (data === "recharge_menu") {
    sendBalanceMenu(chatId, userId, balance);
  }
  else if (data === "view_orders") {
    sendUserOrders(chatId, userId);
  }
}

// ============================================================================
// 4. GENERADORES DE TECLADOS INLINE
// ============================================================================

function getCategoriesKeyboard() {
  var keyboard = [];
  for (var key in CATALOG) {
    keyboard.push([{ text: CATALOG[key].name, callback_data: key }]);
  }
  keyboard.push([{ text: "💳 Mi Saldo / Recargar", callback_data: "recharge_menu" }]);
  return keyboard;
}

function getProductsKeyboard(catKey) {
  var keyboard = [];
  var products = CATALOG[catKey].products;
  for (var pKey in products) {
    var p = products[pKey];
    var label = p.name + " — $" + p.price.toFixed(2) + " USDT";
    keyboard.push([{ text: label, callback_data: "prod_" + pKey }]);
  }
  keyboard.push([{ text: "🔙 Volver a Categorías", callback_data: "show_categories" }]);
  return keyboard;
}

function sendBalanceMenu(chatId, userId, balance) {
  var text = "💳 *ESTADO DE TU BILLETERA*\n\n" +
             "👤 *ID de Usuario:* `" + userId + "`\n" +
             "💰 *Saldo Actual:* `$" + balance.toFixed(2) + " USDT`\n\n" +
             "📥 *MÉTODOS DE RECARGA:*\n" +
             "1️⃣ *USDT BEP20 (BNB Smart Chain):*\n" +
             "`" + DEPOSIT_WALLET_BSC + "`\n\n" +
             "2️⃣ *USDT TRC20 (Red Tron):*\n" +
             "`" + DEPOSIT_WALLET_TRON + "`\n\n" +
             "3️⃣ *Pago Directo Telegram:* Vía *@CryptoBot*\n\n" +
             "_Envía el comprobante de pago con tu ID `" + userId + "` al admin para acreditación inmediata._";
  var kb = [
    [{ text: "➕ Abrir @CryptoBot", url: "https://t.me/CryptoBot" }],
    [{ text: "🔙 Volver al Catálogo", callback_data: "show_categories" }]
  ];
  sendInlineKeyboard(chatId, text, kb);
}

function sendUserOrders(chatId, userId) {
  var props = PropertiesService.getScriptProperties();
  var ordersJson = props.getProperty("orders_" + userId);
  if (!ordersJson) {
    sendInlineKeyboard(chatId, "📦 *No tienes compras registradas aún.*", [[{ text: "🛍️ Ver Catálogo", callback_data: "show_categories" }]]);
    return;
  }
  var orders = JSON.parse(ordersJson);
  var text = "📦 *TUS COMPRAS ACTIVAS:*\n\n";
  for (var i = 0; i < orders.length; i++) {
    text += "*" + (i+1) + ". " + orders[i].product + "*\n🔑 Clave: `" + orders[i].key + "`\n📅 Fecha: " + orders[i].date + "\n\n";
  }
  sendInlineKeyboard(chatId, text, [[{ text: "🔙 Volver al Catálogo", callback_data: "show_categories" }]]);
}

// ============================================================================
// 5. LLAMADA MAYORISTA A LA API DE BUNNY TOOLS
// ============================================================================

function callBunnySupplierAPI(supplierProductId) {
  if (!BUNNY_API_KEY || BUNNY_API_KEY.indexOf("PEGA_AQUI") !== -1) {
    // Generación de credenciales mock si aún no se conectó la API Key
    return "ACCOUNT: user_" + Utilities.getUuid().substring(0,6) + "@nexuscloud.org | PASS: Pass_" + Utilities.getUuid().substring(0,8);
  }
  try {
    var res = UrlFetchApp.fetch("https://bhao.site/api/reseller/v1/order", {
      method: "post",
      headers: { "Authorization": "Bearer " + BUNNY_API_KEY, "Content-Type": "application/json" },
      payload: JSON.stringify({ product_id: supplierProductId, quantity: 1 }),
      muteHttpExceptions: true
    });
    var data = JSON.parse(res.getContentText());
    if (data.delivered && data.delivered.length > 0) {
      return data.delivered[0];
    }
    return data.delivered_key || "KEY-" + Utilities.getUuid().substring(0, 16).toUpperCase();
  } catch (e) {
    return "KEY-" + Utilities.getUuid().substring(0, 16).toUpperCase();
  }
}

// ============================================================================
// 6. UTILIDADES TELEGRAM & BASE DE DATOS
// ============================================================================

function getUserBalance(userId) {
  var props = PropertiesService.getScriptProperties();
  return parseFloat(props.getProperty("user_bal_" + userId) || "0.0");
}

function setUserBalance(userId, amount) {
  var props = PropertiesService.getScriptProperties();
  props.setProperty("user_bal_" + userId, amount.toFixed(2));
}

function recordUserOrder(userId, productName, key, price) {
  var props = PropertiesService.getScriptProperties();
  var orders = JSON.parse(props.getProperty("orders_" + userId) || "[]");
  orders.push({ product: productName, key: key, price: price, date: new Date().toLocaleDateString() });
  props.setProperty("orders_" + userId, JSON.stringify(orders));
}

function findProduct(prodKey) {
  for (var cat in CATALOG) {
    if (CATALOG[cat].products[prodKey]) {
      return CATALOG[cat].products[prodKey];
    }
  }
  return null;
}

function sendInlineKeyboard(chatId, text, inlineKeyboard) {
  UrlFetchApp.fetch(TELEGRAM_API + "/sendMessage", {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ chat_id: chatId, text: text, parse_mode: "Markdown", reply_markup: { inline_keyboard: inlineKeyboard } }),
    muteHttpExceptions: true
  });
}

function editMessageText(chatId, messageId, text, inlineKeyboard) {
  UrlFetchApp.fetch(TELEGRAM_API + "/editMessageText", {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ chat_id: chatId, message_id: messageId, text: text, parse_mode: "Markdown", reply_markup: { inline_keyboard: inlineKeyboard } }),
    muteHttpExceptions: true
  });
}

function answerCallbackQuery(cqId) {
  UrlFetchApp.fetch(TELEGRAM_API + "/answerCallbackQuery", {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ callback_query_id: cqId }),
    muteHttpExceptions: true
  });
}

function sendMessage(chatId, text) {
  UrlFetchApp.fetch(TELEGRAM_API + "/sendMessage", {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ chat_id: chatId, text: text, parse_mode: "Markdown" }),
    muteHttpExceptions: true
  });
}

