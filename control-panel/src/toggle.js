async function toggleGPU() {
    const res = await fetch('/gpu-toggle', { method: 'POST' });
    const data = await res.json();
    document.getElementById('gpu-status').innerText = data.gpu_enabled ? '사용 중' : '사용 안 함';
  }
  
  async function checkGPU() {
    const res = await fetch('/gpu-status');
    const data = await res.json();
    document.getElementById('gpu-status').innerText = data.gpu_enabled ? '사용 중' : '사용 안 함';
  }
  
  async function testTranscribe() {
    const res = await fetch('/transcribe-test', { method: 'POST' });
    const data = await res.json();
    document.getElementById('transcription-result').innerText = data.text || data.error;
  }
  
  window.onload = checkGPU;
  
  async function checkSTTStatus() {
    const cpu = await fetch("/stt-cpu-status").then(r => r.json());
    const gpu = await fetch("/stt-gpu-status").then(r => r.json());

    document.getElementById("stt-cpu-status").innerText = cpu.model_loaded ? "🟢 로드됨" : "🔴 안됨";
    document.getElementById("stt-gpu-status").innerText = gpu.error || (gpu.model_loaded ? "🟢 로드됨" : "🔴 안됨");
}
