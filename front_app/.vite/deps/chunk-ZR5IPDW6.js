import {
  _extends,
  init_extends
} from "./chunk-4KBN3PPH.js";

// node_modules/@mui/base/utils/combineHooksSlotProps.js
init_extends();
function combineHooksSlotProps(getFirstProps, getSecondProps) {
  return function getCombinedProps(external = {}) {
    const firstResult = _extends({}, external, getFirstProps(external));
    const result = _extends({}, firstResult, getSecondProps(firstResult));
    return result;
  };
}

export {
  combineHooksSlotProps
};
//# sourceMappingURL=chunk-ZR5IPDW6.js.map
