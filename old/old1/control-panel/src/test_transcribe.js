async function testTranscribe() {
    const res = await fetch('/transcribe-test', { method: 'POST' });
    const data = await res.json();
    document.getElementById('transcription-result').innerText = data.text || data.error;
}
