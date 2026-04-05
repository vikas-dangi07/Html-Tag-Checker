document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("inputText");
  const checkBtn = document.getElementById("checkBtn");
  const clearBtn = document.getElementById("clearBtn");
  const status = document.getElementById("status");
  const errorsList = document.getElementById("errors");

  function setStatus(ok, msg) {
    status.className = "status " + (ok ? "ok" : "err");
    status.textContent = msg;
  }

  checkBtn.onclick = async () => {
    const text = input.value.trim();
    if (!text) {
      setStatus(false, "Please enter HTML code.");
      errorsList.innerHTML = "";
      return;
    }
    setStatus(false, "Checking...");
    errorsList.innerHTML = "";

    const res = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();

    if (data.ok) {
      setStatus(true, "✅ No tag errors found!");
    } else {
      setStatus(false, `❌ Found ${data.errors.length} issue(s):`);
      data.errors.forEach((err) => {
        const li = document.createElement("li");
        li.textContent = `Line ${err.line}, Col ${err.col}: ${err.message}`;
        errorsList.appendChild(li);
      });
    }
  };

  clearBtn.onclick = () => {
    input.value = "";
    errorsList.innerHTML = "";
    status.className = "status";
    status.textContent = "Cleared.";
  };
});