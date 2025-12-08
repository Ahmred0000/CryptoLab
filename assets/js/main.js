let currentAlgo = "Caesar Cipher";

const algos = {
  "Caesar Cipher": {
    icon: "fa-font",
    title: "Caesar Cipher",
    desc: "Shift substitution.",
    security: "weak",
    controls: `<label>Shift Key:</label><input type="number" id="key" value="3">`,
  },
  "Monoalphabetic Cipher": {
    icon: "fa-random",
    title: "Monoalphabetic Cipher",
    desc: "Alphabet permutation.",
    security: "weak",
    controls: `<label>Key (26 chars):</label><input type="text" id="key" maxlength="26" placeholder="qwertyuiopasdfghjklzxcvbnm">`,
  },
  "Playfair Cipher": {
    icon: "fa-th",
    title: "Playfair Cipher",
    desc: "Digraph substitution using 5x5 matrix. (Includes Visualization)",
    security: "medium",
    controls: `<label>Keyword:</label><input type="text" id="key" placeholder="MONARCHY">`,
  },
  "Hill Cipher": {
    icon: "fa-border-all",
    title: "Hill Cipher",
    desc: "Matrix multiplication.",
    security: "medium",
    controls: `<label>Key Matrix (2x2):</label><div class="matrix-input"><input type="number" class="hill-k" value="5"><input type="number" class="hill-k" value="8"><input type="number" class="hill-k" value="17"><input type="number" class="hill-k" value="3"></div>`,
  },
  "Vigenère Cipher": {
    icon: "fa-italic",
    title: "Vigenère Cipher",
    desc: "Polyalphabetic substitution.",
    security: "medium",
    controls: `<label>Keyword:</label><input type="text" id="key" placeholder="DECEPTIVE">`,
  },
  "One-Time Pad": {
    icon: "fa-file-signature",
    title: "One-Time Pad",
    desc: "Unbreakable if key is random & long.",
    security: "strong",
    controls: `<label>Key (Long as Text):</label><input type="text" id="key" placeholder="Random Key">`,
  },
  "Rail Fence": {
    icon: "fa-bars",
    title: "Rail Fence",
    desc: "Zigzag transposition.",
    security: "weak",
    controls: `<label>Depth:</label><input type="number" id="key" value="2">`,
  },
  "Row Transposition": {
    icon: "fa-table",
    title: "Row Transposition",
    desc: "Columnar transposition.",
    security: "medium",
    controls: `<label>Order (e.g. 3142):</label><input type="text" id="key" placeholder="3142">`,
  },
  "Permutation Cipher": {
    icon: "fa-exchange-alt",
    title: "Permutation Cipher",
    desc: "Block permutation.",
    security: "weak",
    controls: `<label>Key:</label><input type="text" id="key" placeholder="3142">`,
  },
  "Rotor Machines": {
    icon: "fa-cog",
    title: "Rotor Machine",
    desc: "Mechanical substitution.",
    security: "medium",
    controls: `<label>Start Pos:</label><input type="number" id="key" value="5">`,
  },
  "Feistel Cipher": {
    icon: "fa-project-diagram",
    title: "Feistel Cipher",
    desc: "Block cipher structure.",
    security: "medium",
    controls: `<label>Subkey:</label><input type="number" id="key" value="123">`,
  },
  DES: {
    icon: "fa-key",
    title: "DES",
    desc: "Data Encryption Standard.",
    security: "medium",
    controls: `<label>Key (8 chars):</label><input type="text" id="key" maxlength="8" placeholder="12345678">`,
  },
  AES: {
    icon: "fa-lock",
    title: "AES",
    desc: "Advanced Encryption Standard.",
    security: "strong",
    controls: `<label>Key (16 chars):</label><input type="text" id="key" maxlength="16" placeholder="1234567890123456">`,
  },
};

const menuList = document.getElementById("menu-list");
for (const [key, val] of Object.entries(algos)) {
  const li = document.createElement("li");
  li.innerHTML = `<i class="fas ${val.icon}"></i> ${val.title}`;
  li.onclick = () => switchAlgo(key, li);
  menuList.appendChild(li);
}

function switchAlgo(algoName, element) {
  currentAlgo = algoName;
  const config = algos[algoName];

  document.getElementById("algo-title").innerText = config.title;
  document.getElementById("algo-desc").innerText = config.desc;
  document.getElementById("controls-area").innerHTML = config.controls;

  if (element) {
    document
      .querySelectorAll(".nav-links li")
      .forEach((li) => li.classList.remove("active"));
    element.classList.add("active");
  }

  const secFill = document.getElementById("sec-fill");
  const badge = document.getElementById("algo-badge");
  secFill.className = "security-fill";

  if (config.security === "weak") {
    secFill.classList.add("sec-weak");
    badge.style.color = "#ff4b5c";
    badge.innerText = "WEAK";
  } else if (config.security === "medium") {
    secFill.classList.add("sec-med");
    badge.style.color = "#ffce00";
    badge.innerText = "MEDIUM";
  } else {
    secFill.classList.add("sec-strong");
    badge.style.color = "#00ff88";
    badge.innerText = "STRONG";
  }

  document.getElementById("visualization-area").style.display = "none";
  document.getElementById("output-text").value = "";
}

async function process(mode) {
  const text = document.getElementById("input-text").value;
  let key;

  if (currentAlgo === "Hill Cipher") {
    const inputs = document.querySelectorAll(".hill-k");
    key = Array.from(inputs).map((i) => parseInt(i.value) || 0);
  } else if (currentAlgo === "Brute Force Attack") {
    key = 0;
  } else {
    const kInput = document.getElementById("key");
    key = kInput ? kInput.value : "";
  }

  if (!text) {
    alert("Please enter text!");
    return;
  }

  try {
    const response = await fetch("/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ algorithm: currentAlgo, key, text, mode }),
    });
    const data = await response.json();
    document.getElementById("output-text").value = data.result;

    // --- Visualization Logic ---
    if (currentAlgo === "Playfair Cipher" && data.extra && data.extra.matrix) {
      renderGrid(data.extra.matrix);
      if (data.extra.steps) animateSteps(data.extra.steps);
    } else {
      document.getElementById("visualization-area").style.display = "none";
    }
  } catch (error) {
    console.error(error);
    document.getElementById("output-text").value = "Connection Error";
  }
}

function renderGrid(matrix) {
  const area = document.getElementById("visualization-area");
  const grid = document.getElementById("playfair-grid");
  area.style.display = "flex";
  grid.innerHTML = "";

  matrix.forEach((char, index) => {
    const cell = document.createElement("div");
    cell.className = "grid-cell";
    cell.innerText = char;
    cell.id = `cell-${index}`; 
    cell.setAttribute("data-char", char);
    grid.appendChild(cell);
  });
}

function getCellId(char) {
  const cells = document.querySelectorAll(".grid-cell");
  for (let c of cells) {
    if (c.innerText === char) return c.id;
  }
  return null;
}

async function animateSteps(steps) {
  const info = document.getElementById("step-info");

  for (let i = 0; i < steps.length; i++) {
    const s = steps[i];
    info.innerText = `Encrypting Pair: [ ${s.pair[0]} , ${s.pair[1]} ]`;

    const id1 = getCellId(s.pair[0]);
    const id2 = getCellId(s.pair[1]);

    if (id1) document.getElementById(id1).classList.add("highlight-src");
    if (id2) document.getElementById(id2).classList.add("highlight-src");

    await new Promise((r) => setTimeout(r, 800));

    info.innerText += ` ➝ [ ${s.cipher[0]} , ${s.cipher[1]} ]`;
    const id3 = getCellId(s.cipher[0]);
    const id4 = getCellId(s.cipher[1]);

    if (id3) document.getElementById(id3).classList.add("highlight-dest");
    if (id4) document.getElementById(id4).classList.add("highlight-dest");

    await new Promise((r) => setTimeout(r, 1000));

    document.querySelectorAll(".grid-cell").forEach((c) => {
      c.classList.remove("highlight-src", "highlight-dest");
    });
  }
  info.innerText = "Encryption Visualization Complete!";
}

if (menuList.firstChild) switchAlgo("Caesar Cipher", menuList.children[1]);
