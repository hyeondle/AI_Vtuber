// GPU ON/OFF만 담당
async function toggleGPU() {
  const res = await fetch('/gpu-toggle', { method: 'POST' });
  const data = await res.json();
  document.getElementById('gpu-status').innerText = data.gpu_enabled ? '사용 중' : '사용 안 함';
}

window.onload = () => {
  checkGPU();  // 분리된 함수이지만 처음부터 실행되도록 연결
}
