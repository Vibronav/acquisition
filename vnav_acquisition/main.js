'use strict';

/* globals MediaRecorder */
// Spec is at http://dvcs.w3.org/hg/dap/raw-file/tip/media-stream-capture/RecordingProposal.html


const usernameEl = document.getElementById('username');
const iterEl = document.getElementById("iterations");
const startAutomationBt = document.getElementById("startTests");
const stopAutomationBt = document.getElementById("stopTests");
const raspberryStatusEl = document.getElementById("raspberryStatus");
const automationStatusEl = document.getElementById("automationStatus");
const iterationCounterEl = document.getElementById("iterationCounter");

const materialsContainter = document.getElementById("material");
const speedsContainer = document.getElementById("speed");

const audioInputSelect  = document.getElementById("audioSource");
const videoSelect = document.getElementById("videoSource");
const videoSelect2 = document.getElementById("videoSource2");
const selectors = [audioInputSelect, videoSelect, videoSelect2];

const liveVideoElement = document.getElementById('video');
const liveVideoElement2 = document.getElementById('video2');

const spectrogram = document.getElementById('spectrogram');
const ctx = spectrogram.getContext('2d');
const fftSize = 1024;

const waveformCanvasLeft = document.getElementById('micSignalLeft');
const waveformCanvasRight = document.getElementById('micSignalRight');
const waveformCtxLeft = waveformCanvasLeft.getContext('2d');
const waveformCtxRight = waveformCanvasRight.getContext('2d');

const sampleRate = 48000;
const chunkSize = 24000;
const DURATION_SECONDS = 10;
const MAX_BUFFOR_SIZE = sampleRate * DURATION_SECONDS;

liveVideoElement.controls = false;
liveVideoElement2.controls = false;

let localStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let localStream2 = null;
let mediaRecorder2 = null;
let recordedChunks2 = [];
let shouldUpload = true;

let specBuffer = [];
let leftWaveformBuffer = new Float32Array(0);
let rightWaveformBuffer = new Float32Array(0);

const interval = 100;

const fft = new FFT(fftSize, sampleRate);

const DEFAULT_CONFIG = {
	materials: ["slime", "Silicone", "Chicken"],
	speeds: ["slow", "medium", "fast"]
};
const YAXIS_SPECTROGRAM_WIDTH = 55;
const YAXIS_WAVEFORM_WIDTH = 35;

const socket = io();
socket.on("connect", () => {
	console.log("Socket.io connected from browser")
})

socket.on("record", async (msg) => {

	const action = msg.action;
	const filename = msg.filename;
	console.log(action);

	if(!localStream || !localStream2) {
		console.warn("No media stream available to record");
		return;
	}

	if(action === "start") {

		onRecordStart({
			filename: addSuffix(filename, "_cam1"),
			stream: localStream,
			setRecorder: (recorder) => mediaRecorder = recorder,
			setChunks: (chunks) => recordedChunks = chunks,
		});
		onRecordStart({
			filename: addSuffix(filename, "_cam2"),
			stream: localStream2,
			setRecorder: (recorder) => mediaRecorder2 = recorder,
			setChunks: (chunks) => recordedChunks2 = chunks,
		});
		console.log("Browser started recording");

	}

	console.log(mediaRecorder, mediaRecorder2);
	if(action === "stop" && mediaRecorder && mediaRecorder.state === "recording" && mediaRecorder2 && mediaRecorder2.state === "recording") {
		shouldUpload = msg.shouldUpload;
		mediaRecorder.stop();
		mediaRecorder2.stop();
		console.log("Browser stopped recording");
	}

});

socket.on("automation-status", (msg) => {
	const status = msg.status;
	automationStatusEl.textContent = `Automation status: ${status}`;
	automationStatusEl.style.color = status === "running" ? "green" : "red";
	if(status === "running") {
		toggleButtons(true);
	} else {
		toggleButtons(false);
		iterationCounterEl.textContent = `Iteration: -`
	}
});

socket.on("iteration", (msg) => {
	const iterInput = iterEl.value;
	const maxIterations = iterInput ? parseInt(iterInput, 10) || 1 : 1
	const currentIteration = msg.iteration;
	iterationCounterEl.textContent = `Iteration: ${currentIteration} / ${maxIterations}`;
});

socket.on("micro-signal", (msg) => {

	const bufferLeft = new Int32Array(msg.left);
	const bufferRight = new Int32Array(msg.right);
	
	const now = Date.now();

	if (bufferLeft && bufferLeft.length > 0) {

	}
	// if (bufferRight && bufferRight.length > 0) {
	// 	drawWaveform(bufferRight, 'micSignalRight', 'red');
	// }

	if( bufferLeft && bufferLeft.length > 0) {
		processAndDrawSpectrogram(bufferLeft);
	}

})

function mockMicroSignal() {

	const stereo = generateMockStereoSamples();

	const bufferLeft = stereo.filter((_, i) => i % 2 === 0);
	const bufferRight = stereo.filter((_, i) => i % 2 === 1);


	if (bufferLeft && bufferLeft.length > 0) {
		leftWaveformBuffer = updateBuffer(leftWaveformBuffer, bufferLeft);
		drawWaveform(leftWaveformBuffer, waveformCanvasLeft, waveformCtxLeft);
	}
	if (bufferRight && bufferRight.length > 0) {
		rightWaveformBuffer = updateBuffer(rightWaveformBuffer, bufferRight);
		drawWaveform(rightWaveformBuffer, waveformCanvasRight, waveformCtxRight);
	}

	if( bufferLeft && bufferLeft.length > 0) {
		processAndDrawSpectrogram(bufferLeft);
	}
}

function generateMockStereoSamples() {
	const sampleRate = 48000;
	const monoSamples = Math.floor(sampleRate * interval / 1000);
	const totalSamples = monoSamples * 2;
	const stereo = new Int32Array(totalSamples);

	const freqLeft = Math.random() * 300 + 400;
	const ampLeft = Math.random() * 0.5 + 0.2;
	const phaseLeft = Math.random() * 2 * Math.PI;

	const freqRight = Math.random() * 300 + 900;
	const ampRight = Math.random() * 0.5 + 0.2;
	const phaseRight = Math.random() * 2 * Math.PI;

	for (let i = 0; i < monoSamples; i++) {
		const t = i / sampleRate;

		const valLeft = Math.sin(2 * Math.PI * freqLeft * t + phaseLeft);
		const valRight = Math.sin(2 * Math.PI * freqRight * t + phaseRight);

		const noiseL = (Math.random() - 0.5) * 0.05;
		const noiseR = (Math.random() - 0.5) * 0.05;

		const sampleLeft = Math.floor((valLeft * ampLeft + noiseL) * Math.pow(2, 23));
		const sampleRight = Math.floor((valRight * ampRight + noiseR) * Math.pow(2, 23));

		stereo[i * 2] = sampleLeft;
		stereo[i * 2 + 1] = sampleRight;
	}

	return stereo;
}

function updateBuffer(buffer, newChunk) {

	const normFactor = Math.pow(2, 23);

	const normalizedChunk = new Float32Array(newChunk.length);
	for(let i=0; i<newChunk.length; i++) {
		normalizedChunk[i] = newChunk[i];
	}

	let update = new Float32Array(buffer.length + normalizedChunk.length);
	update.set(buffer);
	update.set(normalizedChunk, buffer.length);

	if(update.length > MAX_BUFFOR_SIZE) {
		update = update.slice(update.length - MAX_BUFFOR_SIZE);
	}
	return update;
}

function drawWaveform(buffer, canvas, ctx) {
	const width = canvas.width;
	const height = canvas.height;

	const samplesPerPixel = Math.floor(MAX_BUFFOR_SIZE / width);

	const availableSamples = buffer.length;
	const availablePixels = Math.floor(availableSamples / samplesPerPixel);

	ctx.clearRect(0, 0, width, height);

	drawWaveformLabels(canvas, ctx);

	ctx.beginPath();

	for(let i=0; i<availablePixels; i++) {
		const x = width - 1 - i;

		const start = availableSamples - (i + 1) * samplesPerPixel;
		const end = start + samplesPerPixel;
		const segment = buffer.slice(start, end);

		const min = Math.min(...segment);
		const max = Math.max(...segment);

		const fullScale = Math.pow(2, 23)
		const yMax = (1 - max / fullScale) * height / 2;
		const yMin = (1 - min / fullScale) * height / 2;

		ctx.moveTo(x, yMin);
		ctx.lineTo(x, yMax);

	}

	ctx.strokeStyle = "blue";
	ctx.lineWidth = 1;
	ctx.stroke();

}

function drawWaveformLabels(canvas, ctx) {

	const width = canvas.width;
	const height = canvas.height;
	const fullScale = Math.pow(2, 23);
	const paddingY = 10;
	
	ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
	ctx.font = "10px sans-serif";
	ctx.textAlign = "right";
	ctx.textBaseline = "middle";

	const ticks = [-fullScale, -fullScale / 2, 0, fullScale / 2, fullScale];

	for(let i=0; i<ticks.length; i++) {
		const val = ticks[i];
		
		const rel = val / fullScale;
		const y = paddingY + (1 - (rel + 1) / 2) * (height - 2 * paddingY);

		ctx.fillText(val.toFixed(1), YAXIS_WAVEFORM_WIDTH - 5, y);

		ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
		ctx.beginPath();
		ctx.moveTo(YAXIS_WAVEFORM_WIDTH, y);
		ctx.lineTo(width, y);
		ctx.stroke();
	}

}

function intArrayToHex(intArray) {
	let hexString = "";
	const view = new DataView(new ArrayBuffer(4));
	for(let i=0; i<intArray.length; i++) {
		view.setInt32(0, intArray[i], true);
		const hex = [...new Uint8Array(view.buffer)]
			.map(b => b.toString(16).padStart(2, "0"))
			.reverse()
			.join("");
		hexString += hex;
	}
	return hexString;
}

function hexToInt32Array(hexString) {

	const len = hexString.length / 8;
	const buffer = new ArrayBuffer(len * 4);
	const view = new DataView(buffer);

	for(let i=0; i<len; i++) {
		const hex = hexString.slice(i * 8, i * 8 + 8);
		const int = parseInt(hex, 16);
		const value = int > 0x7FFFFFFF ? int - 0x100000000 : int;
		view.setInt32(i * 4, value, true);
	}

	return new Int32Array(buffer);

}

function average(arr) {
	let sum = 0;
	for (let i=0; i<arr.length; i++) {
		sum += arr[i];
	}
	return sum / arr.length;
}

function processAndDrawSpectrogram(samples) {
	specBuffer = specBuffer.concat(Array.from(samples));

	while(specBuffer.length >= fftSize) {
		const chunk = specBuffer.slice(0, fftSize);
		specBuffer = specBuffer.slice(fftSize / 2);

		const mean = chunk.reduce((sum, x) => sum + x, 0) / chunk.length;
		const centered = chunk.map(x => x - mean);

		const input = new Float32Array(centered.map(x => x / Math.pow(2, 24)));
		fft.forward(input);
		drawColumn(fft.spectrum);
	}
}

function drawColumn(spectrum) {
	const imageData = ctx.getImageData(YAXIS_SPECTROGRAM_WIDTH + 1, 0, spectrogram.width - YAXIS_SPECTROGRAM_WIDTH - 1, spectrogram.height);
	ctx.putImageData(imageData, YAXIS_SPECTROGRAM_WIDTH, 0);

	for (let y=0; y<spectrogram.height; y++) {
		const idx = Math.floor((y / spectrogram.height) * spectrum.length);
		const db = 20 * Math.log10(spectrum[idx] + 1e-6)
		const value = Math.max(0, Math.min(255, db + 100))
		const freq = idx * sampleRate / fftSize
		const color = valueToHSL(value, freq);
		ctx.fillStyle = color;
		ctx.fillRect(spectrogram.width - 1, spectrogram.height - y - 1, 1, 1);
	}
	drawFrequencyLabels();
}

function drawFrequencyLabels() {
	const sampleRate = 48000;
	const fontSize = 10;
	const numTicks = 5;
	const nyquist = sampleRate / 2;
	const padding = 10;
	const labelOffsetX = 2
	const spectrogramWidth = spectrogram.width;
	const spectrogramHeight = spectrogram.height;
	const availableHeight = spectrogramHeight - 2 * padding;

	ctx.font = `${fontSize}px sans-serif`;
	ctx.textAlign = "left";
	ctx.textBaseline = "middle";
	ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
	ctx.fillRect(0, 0, YAXIS_SPECTROGRAM_WIDTH, spectrogram.height);

	ctx.fillStyle = "white";

	ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
	ctx.lineWidth = 1;

	for (let i = 0; i <= numTicks; i++) {
		const rel = i / (numTicks - 1);
		const y = padding + (1 - rel) * availableHeight;
		const freq = Math.round(rel * nyquist);

		ctx.fillText(`${freq} Hz`, labelOffsetX, y);

		ctx.beginPath();
		ctx.moveTo(YAXIS_SPECTROGRAM_WIDTH, y);
		ctx.lineTo(spectrogramWidth, y);
		ctx.stroke();
	}

}

function valueToHSL(value, freq) {
	const clamped = Math.max(0, Math.min(255, value));
	
	const hue = (freq / sampleRate) * sampleRate / 100;
	const saturation = 100;
	const lightness = (clamped / 255) * 50 + 10;

	return `hsl(${hue},${saturation}%,${lightness}%)`;
}

function addSuffix(filename, suffix) {
	const dotIndex = filename.lastIndexOf('.');
	if (dotIndex === -1) {
		return filename + suffix;
	}
	return filename.slice(0, dotIndex) + suffix + filename.slice(dotIndex);
}

function onRecordStart({filename, stream, setRecorder, setChunks}) {

	const chunks = [];

	const recorder = new MediaRecorder(stream, {
		mimeType: "video/webm; codecs=vp9"
	})

	recorder.ondataavailable = (event) => {
		if(event.data.size > 0) {
			chunks.push(event.data);
		}
	}

	recorder.onstop = async () => {
		console.log('stopping');

		if(shouldUpload) {
			const blob = new Blob(chunks, { type: "video/webm" });
			const formData = new FormData();
			formData.append("file", blob, filename);

			await fetch("/upload", {
				method: "POST",
				body: formData
			});
		} else {
			console.warn("Backend forced not to upload video");
		}
	
	}

	recorder.start();
	setRecorder(recorder);
	setChunks(chunks);

}

function renderSelectOptions(selectElement, values) {

	selectElement.innerHTML = "";
	values.forEach(val => {
		const option = document.createElement("option");
		option.value = val;
		option.textContent = val;
		selectElement.appendChild(option);
	})
}

async function loadConfig() {
	try {
		const res = await fetch("/config");
		if(!res.ok) throw new Error();
		return await res.json();
	} catch {
		console.warn("/api/config caused error. Default config to be used")
		return DEFAULT_CONFIG
	}
}

function gotDevices(deviceInfos) {
  // Handles being called several times to update labels. Preserve values.
  const values = selectors.map(select => select.value);
  selectors.forEach((select) => (select.innerHTML = ""));

  console.log(deviceInfos)

  deviceInfos.forEach((info) => {
	const option = document.createElement("option");
	option.value = info.deviceId
	option.text = info.label || `${info.kind}`

	if(info.kind == "audioinput") {
		audioInputSelect.appendChild(option)
	}
	if(info.kind == "videoinput") {
		const option1 = option.cloneNode(true);
		const option2 = option.cloneNode(true);
		videoSelect.appendChild(option1)
		videoSelect2.appendChild(option2)
	}
  });

  selectors.forEach((select, idx) => {
	if([...select.childNodes].some((n) => n.value === values[idx])) {
		select.value = values[idx];
	}
  });
}

function handleError(error) {
  console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
}

// https://github.com/webrtc/samples/tree/gh-pages/src/content/devices/input-output
function startFirstCamera() {
    if (window.stream) {
        window.stream.getTracks().forEach(track => {
          track.stop();
        });
    }
    const audioSource = audioInputSelect.value;
    const videoSource = videoSelect.value;
    const constraints = {
        audio: {deviceId: audioSource ? {exact: audioSource} : undefined},
        video: {
			deviceId: videoSource ? {exact: videoSource} : undefined,
			width:{min:640,ideal:1280,max:1280 },
			height:{ min:480,ideal:720,max:720}, 
			framerate: 60
		}
    };

    navigator.mediaDevices.getUserMedia(constraints)
		.then((stream) => {
			localStream = stream;
			liveVideoElement.srcObject = stream;
			liveVideoElement.play();
		})
		.catch(handleError);
}

function startSecondCamera() {
    if (window.stream) {
        window.stream.getTracks().forEach(track => {
          track.stop();
        });
    }
	const audioSource = audioInputSelect.value;
    const videoSource2 = videoSelect2.value;
    const constraints2 = {
		audio: {deviceId: audioSource ? {exact: audioSource} : undefined},
        video: {
			deviceId: videoSource2 ? {exact: videoSource2} : undefined,
			width:{min:640,ideal:1280,max:1280 },
			height:{ min:480,ideal:720,max:720}, 
			framerate: 60
		}
    };

    navigator.mediaDevices.getUserMedia(constraints2)
		.then((stream) => {
			localStream2 = stream;
			liveVideoElement2.srcObject = stream;
			liveVideoElement2.play();
		})
		.catch(handleError);
}


audioInputSelect.onchange = startFirstCamera;
videoSelect.onchange = startFirstCamera;
videoSelect2.onchange = startSecondCamera;


navigator.mediaDevices.ondevicechange = function(event) {
	log("mediaDevices.ondevicechange");
}

function log(message){
	console.log(message)
}

function toggleButtons(automation_running) {
	startAutomationBt.disabled = automation_running;
	stopAutomationBt.disabled = !automation_running;
}

function startAutomation() {

	const username = usernameEl.value.trim()
	const material = materialsContainter.value;
	const speed = speedsContainer.value;
	const iterInput = iterEl.value;
	const iterations = iterInput ? parseInt(iterInput, 10) || 1 : 1;
	const p1 = [0, 1, 2, 3].map(i => parseInt(document.getElementById(`p1_${i}`).value, 10));
	const p2 = [0, 1, 2, 3].map(i => parseInt(document.getElementById(`p2_${i}`).value, 10));
	const p3 = [0, 1, 2, 3].map(i => parseInt(document.getElementById(`p3_${i}`).value, 10));
	const motionType = document.querySelector('input[name="motionType"]:checked').value;

	if(!username) {
		return alert("Please pass username");
	}
	if(!material) {
		return alert("Please select material");
	}
	if(!speed) {
		return alert("Please select speed");
	}
	if(iterations <= 0) {
		return alert("Iterations must be greater then 0");
	}

	const payload = {
		username: username,
		material: material,
		speed: speed,
		iterations: iterations,
		p1: p1,
		p2: p2,
		p3: p3,
		motionType: motionType,
	};


	fetch("/run", {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify(payload)
	})
	.then(res => {
		if(!res.ok) throw new Error("Server error");
		return res.json();
	})
	.then(data => {
		startAutomationBt.disabled = true;
		console.log("Automation started: ", data);
		alert("Tests started - you can monitor it by video from camera.");
	})
	.catch(err => {
		toggleButtons(false);
		console.error(err);
	})

}

function stopAutomation() {
	

	fetch("/stop", {
		method: "POST"
	})
	.then(res => {
		if(!res.ok) throw new Error("Server error");
		return res.json();
	})
	.then(data => {
		stopAutomationBt.disabled = true;
		console.log("Automation stopped: ", data);
		alert("Tests will be stopped after this iteration.");
	});

}

function updateRaspberryStatus(status) {
	raspberryStatusEl.textContent = `RaspberryPi status: ${status}`;
	raspberryStatusEl.style.color = status === "connected" ? "green" : "red";
}

async function getRaspberryStatus() {
	try {
		const res = await fetch("/raspberry-status");
		const data = await res.json();
		updateRaspberryStatus(data.status);
	} catch (err) {
		console.error("Error fetching RaspberryPi status: ", err);
		updateRaspberryStatus("Not connected");
	}

}

(async function init() {

	const cfg = await loadConfig();
	renderSelectOptions(materialsContainter, cfg.materials);
	renderSelectOptions(speedsContainer, cfg.speeds);

	// for getting devices and permissions
	const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
	stream.getTracks().forEach((t) => t.stop())
	const devices = await navigator.mediaDevices.enumerateDevices();
	gotDevices(devices);
	startFirstCamera();
	startSecondCamera();

})();

startAutomationBt.addEventListener("click", startAutomation);
stopAutomationBt.addEventListener("click", stopAutomation);
setInterval(getRaspberryStatus, 3000);
setInterval(mockMicroSignal, interval);


// Meter class that generates a number correlated to audio volume.
// The meter class itself displays nothing, but it makes the
// instantaneous and time-decaying volumes available for inspection.
// It also reports on the fraction of samples that were at or near
// the top of the measurement range.
function SoundMeter(context) {
  this.context = context;
  this.instant = 0.0;
  this.slow = 0.0;
  this.clip = 0.0;
  this.script = context.createScriptProcessor(2048, 1, 1);
  var that = this;
  this.script.onaudioprocess = function(event) {
	var input = event.inputBuffer.getChannelData(0);
	var i;
	var sum = 0.0;
	var clipcount = 0;
	for (i = 0; i < input.length; ++i) {
	  sum += input[i] * input[i];
	  if (Math.abs(input[i]) > 0.99) {
		clipcount += 1;
	  }
	}
	that.instant = Math.sqrt(sum / input.length);
	that.slow = 0.95 * that.slow + 0.05 * that.instant;
	that.clip = clipcount / input.length;
  };
}

SoundMeter.prototype.connectToSource = function(stream, callback) {
  console.log('SoundMeter connecting');
  try {
	this.mic = this.context.createMediaStreamSource(stream);
	this.mic.connect(this.script);
	// necessary to make sample run, but should not be.
	this.script.connect(this.context.destination);
	if (typeof callback !== 'undefined') {
	  callback(null);
	}
  } catch (e) {
	console.error(e);
	if (typeof callback !== 'undefined') {
	  callback(e);
	}
  }
};
SoundMeter.prototype.stop = function() {
  this.mic.disconnect();
  this.script.disconnect();
};


//browser ID
function getBrowser(){
	var nVer = navigator.appVersion;
	var nAgt = navigator.userAgent;
	var browserName  = navigator.appName;
	var fullVersion  = ''+parseFloat(navigator.appVersion);
	var majorVersion = parseInt(navigator.appVersion,10);
	var nameOffset,verOffset,ix;

	// In Opera, the true version is after "Opera" or after "Version"
	if ((verOffset=nAgt.indexOf("Opera"))!=-1) {
	 browserName = "Opera";
	 fullVersion = nAgt.substring(verOffset+6);
	 if ((verOffset=nAgt.indexOf("Version"))!=-1)
	   fullVersion = nAgt.substring(verOffset+8);
	}
	// In MSIE, the true version is after "MSIE" in userAgent
	else if ((verOffset=nAgt.indexOf("MSIE"))!=-1) {
	 browserName = "Microsoft Internet Explorer";
	 fullVersion = nAgt.substring(verOffset+5);
	}
	// In Chrome, the true version is after "Chrome"
	else if ((verOffset=nAgt.indexOf("Chrome"))!=-1) {
	 browserName = "Chrome";
	 fullVersion = nAgt.substring(verOffset+7);
	}
	// In Safari, the true version is after "Safari" or after "Version"
	else if ((verOffset=nAgt.indexOf("Safari"))!=-1) {
	 browserName = "Safari";
	 fullVersion = nAgt.substring(verOffset+7);
	 if ((verOffset=nAgt.indexOf("Version"))!=-1)
	   fullVersion = nAgt.substring(verOffset+8);
	}
	// In Firefox, the true version is after "Firefox"
	else if ((verOffset=nAgt.indexOf("Firefox"))!=-1) {
	 browserName = "Firefox";
	 fullVersion = nAgt.substring(verOffset+8);
	}
	// In most other browsers, "name/version" is at the end of userAgent
	else if ( (nameOffset=nAgt.lastIndexOf(' ')+1) <
		   (verOffset=nAgt.lastIndexOf('/')) )
	{
	 browserName = nAgt.substring(nameOffset,verOffset);
	 fullVersion = nAgt.substring(verOffset+1);
	 if (browserName.toLowerCase()==browserName.toUpperCase()) {
	  browserName = navigator.appName;
	 }
	}
	// trim the fullVersion string at semicolon/space if present
	if ((ix=fullVersion.indexOf(";"))!=-1)
	   fullVersion=fullVersion.substring(0,ix);
	if ((ix=fullVersion.indexOf(" "))!=-1)
	   fullVersion=fullVersion.substring(0,ix);

	majorVersion = parseInt(''+fullVersion,10);
	if (isNaN(majorVersion)) {
	 fullVersion  = ''+parseFloat(navigator.appVersion);
	 majorVersion = parseInt(navigator.appVersion,10);
	}


	return browserName;
}