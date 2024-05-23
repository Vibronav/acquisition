import {
  useTransitionStateManager
} from "./chunk-XM3NJOAI.js";
import {
  _objectWithoutPropertiesLoose,
  clsx_default,
  init_clsx,
  init_objectWithoutPropertiesLoose
} from "./chunk-L34D2RMA.js";
import {
  _extends,
  init_extends,
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

// node_modules/@mui/base/Transitions/CssAnimation.js
init_extends();
init_objectWithoutPropertiesLoose();
var React = __toESM(require_react());
var import_prop_types = __toESM(require_prop_types());
init_clsx();
var import_jsx_runtime = __toESM(require_jsx_runtime());
var _excluded = ["children", "className", "enterAnimationName", "enterClassName", "exitAnimationName", "exitClassName"];
function CssAnimation(props) {
  const {
    children,
    className,
    enterAnimationName,
    enterClassName,
    exitAnimationName,
    exitClassName
  } = props, other = _objectWithoutPropertiesLoose(props, _excluded);
  const {
    requestedEnter,
    onExited
  } = useTransitionStateManager();
  const hasExited = React.useRef(true);
  React.useEffect(() => {
    if (requestedEnter && hasExited.current) {
      hasExited.current = false;
    }
  }, [requestedEnter]);
  const handleAnimationEnd = React.useCallback((event) => {
    if (event.animationName === exitAnimationName) {
      onExited();
      hasExited.current = true;
    } else if (event.animationName === enterAnimationName) {
      hasExited.current = false;
    }
  }, [onExited, exitAnimationName, enterAnimationName]);
  return (0, import_jsx_runtime.jsx)("div", _extends({
    onAnimationEnd: handleAnimationEnd,
    className: clsx_default(className, requestedEnter ? enterClassName : exitClassName)
  }, other, {
    children
  }));
}
true ? CssAnimation.propTypes = {
  children: import_prop_types.default.node,
  className: import_prop_types.default.string,
  enterAnimationName: import_prop_types.default.string,
  enterClassName: import_prop_types.default.string,
  exitAnimationName: import_prop_types.default.string,
  exitClassName: import_prop_types.default.string
} : void 0;

// node_modules/@mui/base/Transitions/CssTransition.js
init_extends();
init_objectWithoutPropertiesLoose();
var React2 = __toESM(require_react());
var import_prop_types2 = __toESM(require_prop_types());
init_clsx();
var import_jsx_runtime2 = __toESM(require_jsx_runtime());
var _excluded2 = ["children", "className", "lastTransitionedPropertyOnExit", "enterClassName", "exitClassName"];
var CssTransition = React2.forwardRef(function CssTransition2(props, forwardedRef) {
  const {
    children,
    className,
    lastTransitionedPropertyOnExit,
    enterClassName,
    exitClassName
  } = props, other = _objectWithoutPropertiesLoose(props, _excluded2);
  const {
    requestedEnter,
    onExited
  } = useTransitionStateManager();
  const [isEntering, setIsEntering] = React2.useState(false);
  React2.useEffect(() => {
    if (requestedEnter) {
      requestAnimationFrame(() => {
        setIsEntering(true);
      });
    } else {
      setIsEntering(false);
    }
  }, [requestedEnter]);
  const handleTransitionEnd = React2.useCallback((event) => {
    if (!requestedEnter && (lastTransitionedPropertyOnExit == null || event.propertyName === lastTransitionedPropertyOnExit)) {
      onExited();
    }
  }, [onExited, requestedEnter, lastTransitionedPropertyOnExit]);
  return (0, import_jsx_runtime2.jsx)("div", _extends({
    onTransitionEnd: handleTransitionEnd,
    className: clsx_default(className, isEntering ? enterClassName : exitClassName)
  }, other, {
    ref: forwardedRef,
    children
  }));
});
true ? CssTransition.propTypes = {
  children: import_prop_types2.default.node,
  className: import_prop_types2.default.string,
  enterClassName: import_prop_types2.default.string,
  exitClassName: import_prop_types2.default.string,
  lastTransitionedPropertyOnEnter: import_prop_types2.default.string,
  lastTransitionedPropertyOnExit: import_prop_types2.default.string
} : void 0;

export {
  CssAnimation,
  CssTransition
};
//# sourceMappingURL=chunk-QSNBKVJQ.js.map
