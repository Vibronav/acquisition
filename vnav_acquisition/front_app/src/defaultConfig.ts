const defaultConfig = {
  username: "",
  connection: ["raspberrypi.local", 22, "pi", "VibroNav"],
  defaultMaterials: [
    "Slime",
    "Silicone",
    "PU",
    "Plato (play dough)",
    "Plastic",
    "Ikea (plastic bag)",
    "African (silk)"
  ],
  chosenMaterials: [],
  newMaterials: [],
  defaultSpeeds: ["slow", "medium", "fast"],
  chosenSpeeds: [],
  newSpeeds: [],
  local_dir: ".",
  remote_dir: "vnav_acquisition",
  lab_checks: [
    "Quiet room/reduce external noises",
    "Background white Screen",
    "Camera angle",
    "Microphone locations/connections",
    "Material/User/speed info",
    "Test recordings",
    "Gained signal check"
  ],
  chosen_lab_checks: [
    "Quiet room/reduce external noises",
    "Background white Screen",
    "Camera angle",
    "Microphone locations/connections",
    "Material/User/speed info",
    "Test recordings",
    "Gained signal check"
  ],
  new_lab_checks: []

}
export default defaultConfig;