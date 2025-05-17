'use strict';

/* globals MediaRecorder */
// Spec is at http://dvcs.w3.org/hg/dap/raw-file/tip/media-stream-capture/RecordingProposal.html

const recBtn = document.getElementById("rec");
const stopBtn = document.getElementById('stop');
const deleteBtn = document.getElementById('delete');
const usernameEl = document.getElementById('username');

const materialsContainter = document.getElementById("materials");
const speedsContainer = document.getElementById("speeds");

const audioInputSelect  = document.getElementById("audioSource");
const videoSelect = document.getElementById("videoSource");
const selectors = [audioInputSelect, videoSelect];

const liveVideoElement = document.getElementById('video');
const downloadLink = document.getElementById('downloadLink');
const statusLabel = document.getElementById('statusLabel');


liveVideoElement.controls = false;

let localStream = null;
let mediaRecorder = null;
let chunks = [];
let containerType = "video/webm";
let videoFileName = "";

// Helper for now, should be deleted later
const DEFAULT_CONFIG = {
	materials: ["slime", "Silicone", "Chicken"],
	speeds: ["slow", "medium", "fast"]
};

function renderRadioButtons(wrapper, name, values) {

	wrapper.innerHTML = "";
	values.forEach((val, idx) => {
		const id = `${name}-${idx}`;
		const label = document.createElement("label");
		label.setAttribute("for", id);
		label.textContent = val;

		const input = document.createElement("input");
		input.type = "radio";
		input.name = name;
		input.id = id;
		input.value = val;

		wrapper.appendChild(input);
		wrapper.appendChild(label);
		wrapper.appendChild(document.createElement("br"));
	});
}

async function loadConfig() {
	try {
		const res = await fetch("/api/config");
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
	option.value = info.deficeId
	option.text = info.label || `${info.kind} ${option.value}`
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
//    var constraints = {audio:true,video:{width:{min:640,ideal:640,max:640 },height:{ min:480,ideal:480,max:480},framerate:60}};

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

function onRecord(){
	const username = usernameEl.value.trim()
	const material = document.querySelector('input[name="materials"]:checked')
	const speed = document.querySelector('input[name="speeds"]:checked')

	if(!localStream) {
		alert('Could not get local stream from mic/camera');
	} 
	if(!username) {
		alert('Please input user name');
	}
	if(!material) {
		alert('Please select material');
	}
	if(!speed) {
		alert('Please select speed');
	}

	recBtn.disabled = true;
	recBtn.textContent = 'Recording...';
	stopBtn.disabled = false;
	statusLabel.textContent = 'Comunicating with RaspberryPi...';

	/* use the stream */
	log('Start recording...');
	fetch("/start", {
		method: "POST",
		body: JSON.stringify({
			username: username.value,
			material: material.value,
			speed: speed.value
		}),
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	})
		.then(res => res.json())
		.then(filename => {
			videoFileName = filename;
			console.log(filename)
			statusLabel.textContent = `Recording started (${filename})`;
		});

	

	if (typeof MediaRecorder.isTypeSupported == 'function'){
		/*
			MediaRecorder.isTypeSupported is a function announced in https://developers.google.com/web/updates/2016/01/mediarecorder and later introduced in the MediaRecorder API spec http://www.w3.org/TR/mediastream-recording/
		*/
		if (MediaRecorder.isTypeSupported('video/mp4')) {
			//Safari 14.0.2 has an EXPERIMENTAL version of MediaRecorder enabled by default
			containerType = "video/mp4";
			var options = {mimeType: 'video/mp4'};
		} else if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) {
			var options = {mimeType: 'video/webm;codecs=vp9'};
		} else if (MediaRecorder.isTypeSupported('video/webm;codecs=h264')) {
			var options = {mimeType: 'video/webm;codecs=h264'};
		} else if (MediaRecorder.isTypeSupported('video/webm')) {
			var options = {mimeType: 'video/webm'};
		}
		log('Using '+options.mimeType);
		mediaRecorder = new MediaRecorder(localStream, options);
	}else{
		log('isTypeSupported is not supported, using default codecs for browser');
		mediaRecorder = new MediaRecorder(localStream);
	}

	chunks = [];

	mediaRecorder.ondataavailable = function(e) {
		log('mediaRecorder.ondataavailable, e.data.size='+e.data.size);
		if (e.data && e.data.size > 0) {
			chunks.push(e.data);
		}
	};

	mediaRecorder.onerror = function(e){
		log('mediaRecorder.onerror: ' + e);
	};

	mediaRecorder.onstart = function(){
		log('mediaRecorder.onstart, mediaRecorder.state = ' + mediaRecorder.state);
		
		localStream.getTracks().forEach(function(track) {
			if(track.kind == "audio"){
			log("onstart - Audio track.readyState="+track.readyState+", track.muted=" + track.muted);
			}
			if(track.kind == "video"){
			log("onstart - Video track.readyState="+track.readyState+", track.muted=" + track.muted);
			}
		});
		
	};

	mediaRecorder.onpause = function(){
		log('mediaRecorder.onpause, mediaRecorder.state = ' + mediaRecorder.state);
	}

	mediaRecorder.onresume = function(){
		log('mediaRecorder.onresume, mediaRecorder.state = ' + mediaRecorder.state);
	}

	mediaRecorder.onwarning = function(e){
		log('mediaRecorder.onwarning: ' + e);
	};

	mediaRecorder.onstop = onRecorderStop;

	mediaRecorder.start(1000);

	localStream.getTracks().forEach(function(track) {
		log(track.kind+":"+JSON.stringify(track.getSettings()));
		console.log(track.getSettings());
	})

}

navigator.mediaDevices.ondevicechange = function(event) {
	log("mediaDevices.ondevicechange");
}

function onRecorderStop() {
	const blob = new Blob(chunks, {type: mediaRecorder.mimeType});
	const url = URL.createObjectURL(blob);
	const ext = containerType == "video/mp4" ? "mp4" : "webm";
	const name = `${videoFileName}.${ext}`

	downloadLink.hidden = false;
	downloadLink.href = url;
	downloadLink.download = name;
	downloadLink.textContent = `Download recording ${name}`;

	fetch("/stop")
		.then((res) => res.json())
		.then((res) => {
			statusLabel.textContent = res.length
				? "Recording saved successfully"
				: "Recording save failed"
		});
}

function onStop(){
	mediaRecorder?.stop();
	recBtn.disabled = false;
	recBtn.innerHTML = 'Record';
	stopBtn.disabled = true;
    deleteBtn.disabled = false;
}

function onDelete(){
    fetch("/delete_last")
    .then(res => res.json())
    .then(files => {
        if(files.length) {
			statusLabel.textContent = "Deleted: " + files.join(", ");
			deleteBtn.disabled = true;
		}
    })
}


function log(message){
	// dataElement.innerHTML = dataElement.innerHTML+'<br>'+message ;
	console.log(message)
}

(async function init() {

	const cfg = await loadConfig();
	renderRadioButtons(materialsContainter, "materials", cfg.materials);
	renderRadioButtons(speedsContainer, "speeds", cfg.speeds);

	// for getting devices and permissions
	const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
	stream.getTracks().forEach((t) => t.stop())
	const devices = await navigator.mediaDevices.enumerateDevices();
	gotDevices(devices);
	start();

})();

recBtn.addEventListener("click", onRecord);
stopBtn.addEventListener("click", onStop);
deleteBtn.addEventListener("click", onDelete);

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