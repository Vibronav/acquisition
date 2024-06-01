const defaultConfig = {
  username: "",
  connection: ["raspberrypi", 22, "pi", "VibroNav"],
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
  local_dir: "c:\\vnav_acquisition",
  remote_dir: "vnav_acquisition"

}
export default defaultConfig;