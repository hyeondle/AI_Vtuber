async function checkGPU() {
    const res = await fetch('/gpu-status');
    const data = await res.json();
    document.getElementById('gpu-status').innerText = data.gpu_enabled ? '사용 중' : '사용 안 함';
}

async function checkSTTStatus() {
    const cpu = await fetch("/stt-cpu-status").then(r => r.json());
    const gpu = await fetch("/stt-gpu-status").then(r => r.json());

    document.getElementById("stt-cpu-status").innerText = cpu.model_loaded ? "🟢 로드됨" : "🔴 안됨";
    document.getElementById("stt-gpu-status").innerText = gpu.error || (gpu.model_loaded ? "🟢 로드됨" : "🔴 안됨");
}
