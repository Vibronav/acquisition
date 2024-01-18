'use strict';

/* globals MediaRecorder */
// Spec is at http://dvcs.w3.org/hg/dap/raw-file/tip/media-stream-capture/RecordingProposal.html

var recBtn = document.querySelector('button#rec');
var stopBtn = document.querySelector('button#stop');
var deleteBtn = document.querySelector('button#delete');
var username = document.getElementById('username')

var liveVideoElement = document.querySelector('#video');
var dataElement = document.querySelector('#data');
var downloadLink = document.querySelector('a#downloadLink');
var statusLabel = document.querySelector('div#statusLabel');

const audioInputSelect = document.querySelector('select#audioSource');
const videoSelect = document.querySelector('select#videoSource');
const selectors = [audioInputSelect, videoSelect];

liveVideoElement.controls = false;

var mediaRecorder;
var chunks = [];
var count = 0;
var localStream = null;
var soundMeter  = null;
var containerType = "video/webm";
var videoFileName = ""


function gotDevices(deviceInfos) {
  // Handles being called several times to update labels. Preserve values.
  const values = selectors.map(select => select.value);
  selectors.forEach(select => {
    while (select.firstChild) {
      select.removeChild(select.firstChild);
    }
  });
  console.log(deviceInfos)
  for (let i = 0; i !== deviceInfos.length; ++i) {
    const deviceInfo = deviceInfos[i];
    const option = document.createElement('option');
    option.value = deviceInfo.deviceId;
    if (deviceInfo.kind === 'audioinput') {
      console.log(deviceInfo)
      option.text = deviceInfo.label || `microphone ${audioInputSelect.length + 1}`;
      audioInputSelect.appendChild(option);
    } else if (deviceInfo.kind === 'videoinput') {
      option.text = deviceInfo.label || `camera ${videoSelect.length + 1}`;
      videoSelect.appendChild(option);
    } else {
      console.log('Some other kind of source/device: ', deviceInfo);
    }
  }
  selectors.forEach((select, selectorIndex) => {
    if (Array.prototype.slice.call(select.childNodes).some(n => n.value === values[selectorIndex])) {
      select.value = values[selectorIndex];
    }
  });
}

navigator.mediaDevices
    .getUserMedia({ audio: true, video: true })
    .then((s) => {
        navigator.mediaDevices.enumerateDevices().then(gotDevices).then(start).catch(handleError);
    });

audioInputSelect.onchange = start;
videoSelect.onchange = start;

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
        video: {deviceId: videoSource ? {exact: videoSource} : undefined, width:{min:640,ideal:1280,max:1280 },height:{ min:480,ideal:720,max:720}, framerate: 60}
    };
//    var constraints = {audio:true,video:{width:{min:640,ideal:640,max:640 },height:{ min:480,ideal:480,max:480},framerate:60}};

    if (!navigator.mediaDevices.getUserMedia){
        alert('navigator.mediaDevices.getUserMedia not supported on your browser, use the latest version of Firefox or Chrome');
    } else{
        if (window.MediaRecorder == undefined) {
                alert('MediaRecorder not supported on your browser, use the latest version of Firefox or Chrome');
        }else{
            navigator.mediaDevices.getUserMedia(constraints)
                .then(function(stream) {
                    localStream = stream;

                    localStream.getTracks().forEach(function(track) {
                        if(track.kind == "audio"){
                            track.onended = function(event){
                                 log("audio track.onended Audio track.readyState="+track.readyState+", track.muted=" + track.muted);
                            }
                        }
                        if(track.kind == "video"){
                            track.onended = function(event){
                                log("video track.onended Audio track.readyState="+track.readyState+", track.muted=" + track.muted);
                            }
                        }
                    });

                    liveVideoElement.srcObject = localStream;
                    liveVideoElement.play();

                    try {
                        window.AudioContext = window.AudioContext || window.webkitAudioContext;
                        window.audioContext = new AudioContext();
                    } catch (e) {
                        log('Web Audio API not supported.');
                    }

                    soundMeter = window.soundMeter = new SoundMeter(window.audioContext);
                    soundMeter.connectToSource(localStream, function(e) {
                        if (e) {
                            log(e);
                            return;
                        }
                    });

                }).catch(function(err) {
                    /* handle the error */
                    log('navigator.getUserMedia error: '+err);
                });
        }
    }
}


function onBtnRecordClicked(){
	let material = document.querySelector('input[name="material"]:checked')
	let speed = document.querySelector('input[name="speed"]:checked')
	if (localStream == null) {
		alert('Could not get local stream from mic/camera');
	} else if (username.value == "") {
		alert('Please input user name');
	} else if (material == null) {
		alert('Please select material');
	} else if (speed == null) {
		alert('Please select speed');
	} else {
		recBtn.disabled = true;
		recBtn.innerHTML = 'Recording...';
        stopBtn.disabled = false;
        statusLabel.innerHTML = '<font color="orange">Communicating with RaspberryPi...</font>';

		chunks = [];

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
        }).then(res => res.json()).then(res => {
            videoFileName = res;
            console.log(res)
            statusLabel.innerHTML = `<font color="blue">Recording started (${res})</font>`;
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

		mediaRecorder.onstop = function(){
			log('mediaRecorder.onstop, mediaRecorder.state = ' + mediaRecorder.state);

			var recording = new Blob(chunks, {type: mediaRecorder.mimeType});
			downloadLink.href = URL.createObjectURL(recording);

			var rand =  Math.floor((Math.random() * 10000000));
			switch(containerType){
				case "video/mp4":
					var name  = videoFileName + ".mp4" ;
					break;
				default:
					var name  = videoFileName + ".webm" ;
			}

			downloadLink.innerHTML = '<br> Download recording '+name;

			downloadLink.setAttribute( "download", name);
			downloadLink.setAttribute( "name", name);
			downloadLink.click();

			fetch("/stop").then(res => res.json()).then(res => {
                var recordingStatus = res;
                if (recordingStatus.length){
                    const recorded_files = recordingStatus.join('<br>')
                    statusLabel.innerHTML = `<font color="green">Recording saved succesfully to local directory:<br>${recorded_files}</font>`;
                } else {
                    statusLabel.innerHTML = '<font color="red">Recording save failed.</font>';
                }
                console.log(res)
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

		// pauseResBtn.textContent = "Pause";

		mediaRecorder.start(1000);

		localStream.getTracks().forEach(function(track) {
			log(track.kind+":"+JSON.stringify(track.getSettings()));
			console.log(track.getSettings());
		})
	}
}

navigator.mediaDevices.ondevicechange = function(event) {
	log("mediaDevices.ondevicechange");
}

function onBtnStopClicked(){
	mediaRecorder.stop();
	recBtn.disabled = false;
	recBtn.innerHTML = 'Record';
	stopBtn.disabled = true;
    deleteBtn.disabled = false;
}

function onBtnDeteleClicked(){
    fetch("/delete_last")
    .then(res => res.json())
    .then(res => {
        var recordingStatus = res;
        if (recordingStatus){
            const deleted_files = recordingStatus.join('<br>')
            statusLabel.innerHTML = `<font color="purple">Last recording deleted:<br>${deleted_files}</font>`;
            deleteBtn.disabled = true;
        }
    })
}


function log(message){
	// dataElement.innerHTML = dataElement.innerHTML+'<br>'+message ;
	console.log(message)
}

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
