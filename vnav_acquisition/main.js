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
const selectors = [audioInputSelect, videoSelect];

const liveVideoElement = document.getElementById('video');

liveVideoElement.controls = false;

let localStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let shouldUpload = true;

const socket = io();
socket.on("connect", () => {
	console.log("Socket.io connected from browser")
})

socket.on("record", async (msg) => {

	const action = msg.action;
	const filename = msg.filename;
	console.log(action);

	if(!localStream) {
		console.warn("No media stream available to record");
		return;
	}

	if(action === "start") {

		if(mediaRecorder && mediaRecorder.state === "recording") {
			console.warn("Already recording");
			return;			
		}

		recordedChunks = [];

		mediaRecorder = new MediaRecorder(localStream, {
			mimeType: "video/webm; codecs=vp9"
		})

		mediaRecorder.ondataavailable = (event) => {
			if(event.data.size > 0) {
				recordedChunks.push(event.data);
			}
		}

		mediaRecorder.onstop = async () => {
			console.log('stopping');

			if(shouldUpload) {
				const blob = new Blob(recordedChunks, { type: "video/webm" });
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

		mediaRecorder.start();
		console.log("Browser started recording");

	}

	if(action === "stop" && mediaRecorder && mediaRecorder.state === "recording") {
		shouldUpload = msg.shouldUpload;
		mediaRecorder.stop();
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

const DEFAULT_CONFIG = {
	materials: ["slime", "Silicone", "Chicken"],
	speeds: ["slow", "medium", "fast"]
};

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
		videoSelect.appendChild(option)
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
function start() {
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


audioInputSelect.onchange = start;
videoSelect.onchange = start;


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
	start();

})();

startAutomationBt.addEventListener("click", startAutomation);
stopAutomationBt.addEventListener("click", stopAutomation);
setInterval(getRaspberryStatus, 5000);


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