import {
  useDropdown
} from "./chunk-2AMXISCR.js";
import {
  DropdownContext
} from "./chunk-CY7GVJQH.js";
import {
  exactProp,
  init_utils
} from "./chunk-W65C2TNS.js";
import {
  require_jsx_runtime
} from "./chunk-4KBN3PPH.js";
import {
  require_prop_types
} from "./chunk-RD4YHGOG.js";
import {
  require_react
} from "./chunk-UM3JHGVO.js";
import {
  __toESM
} from "./chunk-CEQRFMJQ.js";

// node_modules/@mui/base/Dropdown/Dropdown.js
var React = __toESM(require_react());
var import_prop_types = __toESM(require_prop_types());
init_utils();
var import_jsx_runtime = __toESM(require_jsx_runtime());
function Dropdown(props) {
  const {
    children,
    open,
    defaultOpen,
    onOpenChange
  } = props;
  const {
    contextValue
  } = useDropdown({
    defaultOpen,
    onOpenChange,
    open
  });
  return (0, import_jsx_runtime.jsx)(DropdownContext.Provider, {
    value: contextValue,
    children
  });
}
true ? Dropdown.propTypes = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │ To update them, edit the TypeScript types and run `pnpm proptypes`. │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * @ignore
   */
  children: import_prop_types.default.node,
  /**
   * If `true`, the dropdown is initially open.
   */
  defaultOpen: import_prop_types.default.bool,
  /**
   * Callback fired when the component requests to be opened or closed.
   */
  onOpenChange: import_prop_types.default.func,
  /**
   * Allows to control whether the dropdown is open.
   * This is a controlled counterpart of `defaultOpen`.
   */
  open: import_prop_types.default.bool
} : void 0;
if (true) {
  Dropdown["propTypes"] = exactProp(Dropdown.propTypes);
}

export {
  Dropdown
};
//# sourceMappingURL=chunk-TPT4PXJT.js.map
