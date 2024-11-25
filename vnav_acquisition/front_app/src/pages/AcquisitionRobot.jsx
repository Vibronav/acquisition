import { FormControl, InputLabel, MenuItem, Select, Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import { useState } from 'react';
import { FormattedMessage } from 'react-intl';
import LabChecklist from '../components/LabChecklist.jsx';
import RecordingButtons from '../components/RecordingButtonsDobot.jsx';
import VideoAudioSelect from '../components/VideoAudioSelect.jsx';
import { formControlStyles, selectStyles } from './../themes';
import DobotController  from '../components/DobotController.jsx';
import { useEffect } from 'react';



const AcquisitionRobot = ({ config }) => {
    // State variables
    const [selectedVideoDevices, setSelectedVideoDevices] = useState([]); // Selected video devices state
    const [videoDevices, setVideoDevices] = useState([]); // Video devices state
    const [selectedMaterial, setSelectedMaterial] = useState(null);
    const [selectedSpeed, setSelectedSpeed] = useState(null);
    const [measurementCounter, setMeasurementCounter] = useState(0);
    const [audioFiles, setAudioFiles] = useState([]);  //audio files recorded 
    const [recordingStatus, setRecordingStatus] = useState("init");
    const initalComment = sessionStorage.getItem("commentAcquisiton") || ''
    const [comment, setComment] = useState(initalComment);
    const [P1, setP1] = useState({ x: '350', y: '0', z: '70' });
    const [P2, setP2] = useState({ x: '350', y: '0', z: '70' });
    const [P3, setP3] = useState({ x: '350', y: '0', z: '20' });
    const [positionType, setPositionType] = useState('Only Up and Down');
    const [numIterations, setNumIterations] = useState('22');


    const handleMaterialChange = (event) => {
        setSelectedMaterial(event.target.value)
    }

    const handleSpeedChange = (event) => {
        setSelectedSpeed(event.target.value)
    }

    useEffect(() => {
        sessionStorage.setItem("commentAcquisiton",comment)
      },[comment])

    console.log("Acq Robot", config)
    return (
        <div>


            <Stack sx={{ width: '100%', gap: 5 }} direction="row">

                <Stack sx={{ width: '100%', gap: 5 }} direction="row">
                    <Stack sx={{ gap: 3, width: '40%' }} >

                    <Typography id="username" labelId="usernameLabel" variant="h6" >
                        <FormattedMessage id="username" />: {config.username}</Typography>


                    {/*Video device selection + material selection + speed selection */}
                    <Stack sx={{ width: '100%', gap: 2 }}>
                        {/* Video and audio selection component */}
                        <VideoAudioSelect
                            selectedVideoDevices={selectedVideoDevices}
                            setSelectedVideoDevices={setSelectedVideoDevices}
                            videoDevices={videoDevices}
                            setVideoDevices={setVideoDevices}

                        />

                        {/* Stack for  material, and speed selection */}
                        <Stack sx={{ width: '100%', gap: 2 }}>

                            <FormControl
                                sx={formControlStyles} >
                                <InputLabel>
                                    {<FormattedMessage id="Material" />}
                                </InputLabel>
                                <Select
                                    sx={selectStyles}
                                    labelId="materialSelect"
                                    label="Material"
                                    id="material"
                                    value={selectedMaterial}
                                    onChange={handleMaterialChange}

                                >
                                    {/* Render material options */}
                                    {config.chosenMaterials.filter(value => value !== 0).map((material) => (
                                        <MenuItem key={material} value={material}>
                                            {material}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <FormControl
                                sx={formControlStyles} >
                                <InputLabel>
                                    <FormattedMessage id="speed"></FormattedMessage>
                                </InputLabel>
                                <Select
                                    sx={selectStyles}
                                    labelId="materialSelect"
                                    label="Speed"
                                    id="speed"
                                    value={selectedSpeed}
                                    onChange={handleSpeedChange}
                                >
                                    {/* Render speed options */}
                                    {config.chosenSpeeds.filter(value => value !== 0).map((speeds) => (
                                        <MenuItem key={speeds} value={speeds}>
                                            {speeds}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                        </Stack>

                    </Stack>
                    <Stack sx={{ width: '100%' }}>
                        <LabChecklist config={config} />

                    </Stack>


                    <Typography>
                        <FormattedMessage id="performedMeasurements" />
                        : {measurementCounter}
                    </Typography>
                    {/* <Typography variant="h6">
                    <FormattedMessage id="comment"/>
                        <TextareaAutosize   
                            style={{ width: '100%' }} 
                            value={comment} 
                            minRows={4}
                            maxRows={10}
                            onChange={(() => {setComment(event.target.value)})}
                        />
                    </Typography> */}
                    </Stack>
                    <Stack sx={{ gap: 3, width: '50%' }} >
                        <DobotController 
                            config={config}
                            positionType={positionType}
                            P1={P1}
                            P2={P2} 
                            P3={P3}
                            numIterations={numIterations}
                            setP1={setP1}
                            setP2={setP2}
                            setP3={setP3}
                            setPositionType={setPositionType}
                            setNumIterations={setNumIterations}>
                        </DobotController> 
                    </Stack>
                </Stack>
                
                {/* Stack for video recording controls */}
                <Stack
                    sx={{width: '50%'}} mt={1} spacing={2} >

                    {/* {recordingStatus !== "start" && recordingStatus !== "init" &&
                        audioFiles.map((file, index) => (
                            <AudioPlayer key={index} audioUrl={file.url} />
                        ))
                    } */}

                    <RecordingButtons
                        username={config.username}
                        material={selectedMaterial}
                        speed={selectedSpeed}
                        positionType={positionType}
                        P1={P1}
                        P2={P2} 
                        P3={P3}
                        numIterations={numIterations}
                        measurementCounter={measurementCounter}
                        setMeasurementCounter={setMeasurementCounter}
                        selectedVideoDevices={selectedVideoDevices}
                        videoDevices={videoDevices}
                        audioFiles={audioFiles}
                        setAudioFiles={setAudioFiles}
                        setRecordingStatus={setRecordingStatus}
                        localDir={config.local_dir}
                    />
                </Stack>

            </Stack>


        </div >
    );
}

AcquisitionRobot.propTypes = {
    config: PropTypes.object.isRequired
};

export default AcquisitionRobot;
