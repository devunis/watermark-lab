const $ = (id) => document.getElementById(id);

const modelName = $("modelName");
const toast = $("toast");
let toastTimer;

function notify(message, error = false) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.className = `toast show${error ? " error" : ""}`;
  toastTimer = setTimeout(() => { toast.className = "toast"; }, 3200);
}

async function api(path, payload) {
  const response = await fetch(path, {
    method: payload ? "POST" : "GET",
    headers: payload ? { "content-type": "application/json" } : {},
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

async function withBusy(button, label, action) {
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = label;
  try { await action(); }
  catch (error) { notify(error.message, true); }
  finally { button.disabled = false; button.innerHTML = original; }
}

function sharedText() {
  return $("detectText").value.trim() || $("generatedText").textContent.trim();
}

function detectPayload(text) {
  return { text, model_name: modelName.value };
}

function renderDetection(data) {
  $("detectMetrics").classList.remove("hidden");
  const verdict = $("verdict");
  verdict.className = `verdict ${data.detected ? "detected" : "clear"}`;
  verdict.querySelector("strong").textContent = data.detected ? "DETECTED" : "NO SIGNAL";
  $("zScore").textContent = Number(data.z_score).toFixed(2);
  $("greenFraction").textContent = `${(Number(data.green_fraction) * 100).toFixed(1)}%`;
  $("tokensAnalyzed").textContent = data.tokens_analyzed;
}

$("generateButton").addEventListener("click", () => withBusy($("generateButton"), "모델 생성 중…", async () => {
  const data = await api("/generate", {
    prompt: $("prompt").value,
    model_name: modelName.value,
    max_new_tokens: Number($("maxTokens").value),
    seed: Number($("seed").value),
  });
  $("generatedText").textContent = data.text;
  $("detectText").value = data.text;
  $("generateResult").classList.remove("hidden");
  notify("워터마크 텍스트가 생성되었습니다.");
}));

$("detectButton").addEventListener("click", () => withBusy($("detectButton"), "신호 분석 중…", async () => {
  const text = sharedText();
  if (!text) throw new Error("분석할 텍스트를 입력하세요.");
  renderDetection(await api("/detect", detectPayload(text)));
}));

$("copyGenerated").addEventListener("click", async () => {
  await navigator.clipboard.writeText($("generatedText").textContent);
  notify("생성 텍스트를 복사했습니다.");
});

$("intensity").addEventListener("input", (event) => {
  $("intensityValue").textContent = `${event.target.value}%`;
});

function stressPayload() {
  const text = sharedText();
  if (!text) throw new Error("먼저 생성하거나 검사할 텍스트를 입력하세요.");
  const intensity = Number($("intensity").value) / 100;
  return {
    ...detectPayload(text),
    attack: $("attack").value,
    synonym_probability: intensity,
    noise_probability: intensity,
    truncation_fraction: Math.max(.2, 1 - intensity),
    authorized_self_test: $("authorized").checked,
  };
}

$("stressButton").addEventListener("click", () => withBusy($("stressButton"), "내구성 측정 중…", async () => {
  if (!$("authorized").checked) throw new Error("자체 워터마크 테스트 확인란을 선택하세요.");
  const data = await api("/stress-test", stressPayload());
  $("scoreCompare").classList.remove("hidden");
  $("beforeScore").textContent = Number(data.before.z_score).toFixed(2);
  $("afterScore").textContent = Number(data.after.z_score).toFixed(2);
  $("signalDrop").textContent = Number(data.signal_drop).toFixed(2);
  $("beforeBar").style.width = `${Math.min(100, Math.max(0, data.before.z_score * 10))}%`;
  $("afterBar").style.width = `${Math.min(100, Math.max(0, data.after.z_score * 10))}%`;
  $("transformedText").textContent = data.transformed_text;
  $("stressResult").classList.remove("empty");
  $("benchmarkList").classList.add("hidden");
}));

$("benchmarkButton").addEventListener("click", () => withBusy($("benchmarkButton"), "4개 공격 실행 중…", async () => {
  const payload = stressPayload();
  const data = await api("/benchmark", payload);
  const list = $("benchmarkList");
  list.innerHTML = data.cases.map((item) => `
    <div class="benchmark-item ${item.result.detected ? "detected" : ""}">
      <span>${item.name.toUpperCase()}</span>
      <strong>z ${Number(item.result.z_score).toFixed(2)}</strong>
    </div>`).join("");
  list.classList.remove("hidden");
  notify(`변형 후 검출률 ${(data.detection_rate_after_attack * 100).toFixed(0)}%`);
}));

api("/health").then(() => {
  $("connection").classList.add("online");
  $("connection").innerHTML = "<span></span> API ONLINE";
}).catch(() => {
  $("connection").innerHTML = "<span></span> API OFFLINE";
});
