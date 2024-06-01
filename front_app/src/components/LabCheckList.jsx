import * as React from 'react';
import PropTypes from 'prop-types';
import { Dropdown } from '@mui/base/Dropdown';
import { Menu } from '@mui/base/Menu';
import { MenuButton as BaseMenuButton } from '@mui/base/MenuButton';
import { MenuItem as BaseMenuItem, menuItemClasses } from '@mui/base/MenuItem';
import { styled } from '@mui/system';
import { CssTransition } from '@mui/base/Transitions';
import { PopupContext } from '@mui/base/Unstable_Popup';
import { Container, Checkbox } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import ErrorIcon from '@mui/icons-material/Error';

export default function LabChecklist({ config }) {
  const [tasks, setTasks] = React.useState(config.chosen_lab_checks);

  React.useEffect(() => {
    setTasks(config.chosen_lab_checks);
  }, [config]);

  const [checkedItems, setCheckedItems] = React.useState(() =>
    (config.chosen_lab_checks || []).reduce((acc, task) => {
      acc[task] = false;
      return acc;
    }, {})
  );

  const createHandleCheckboxChange = (item) => (event) => {
    setCheckedItems((prevState) => ({
      ...prevState,
      [item]: event.target.checked,
    }));
  };

  const allChecked = tasks.length > 0 && tasks.every(task => checkedItems[task]);

  return (
    <Container sx={{ width: '100%', justifyContent: 'right', display: 'flex' }}>
      <Dropdown>
        <MenuButton sx={{ width: '100%', display: "flex", alignItems: "center", justifyContent:"center", gap: 1 }} allChecked={allChecked}>
          Before Measurement Checklist
          {allChecked ?
            <CheckIcon /> :
            <ErrorIcon />
          }
        </MenuButton>
        <Menu slots={{ listbox: AnimatedListbox }}>
          {tasks.map((task) => (
            <MenuItem key={task} onClick={createHandleCheckboxChange(task)}>
              <Checkbox checked={!!checkedItems[task]} onChange={createHandleCheckboxChange(task)} />
              {task}
            </MenuItem>
          ))}
        </Menu>
      </Dropdown>
    </Container>
  );
}

LabChecklist.propTypes = {
  config: PropTypes.shape({
    chosen_lab_checks: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
};

const Listbox = styled('ul')(
  ({ theme }) => `
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.875rem;
  box-sizing: border-box;
  padding: 6px;
  margin: 12px 0;
  min-width: 200px;
  border-radius: 12px;
  overflow: auto;
  outline: 0px;
  z-index: 1;
  background-color: ${theme.palette.background.paper};
  color: ${theme.palette.text.primary};

  .closed & {
    opacity: 0;
    transform: scale(0.95, 0.8);
    transition: opacity 200ms ease-in, transform 200ms ease-in;
  }
  
  .open & {
    opacity: 1;
    transform: scale(1, 1);
    transition: opacity 100ms ease-out, transform 100ms cubic-bezier(0.43, 0.29, 0.37, 1.48);
  }

  .placement-top & {
    transform-origin: bottom;
  }

  .placement-bottom & {
    transform-origin: top;
  }
  `,
);

const AnimatedListbox = React.forwardRef(function AnimatedListbox(props, ref) {
  const { ownerState, ...other } = props;
  const popupContext = React.useContext(PopupContext);

  if (popupContext == null) {
    throw new Error(
      'The `AnimatedListbox` component cannot be rendered outside a `Popup` component',
    );
  }

  const verticalPlacement = popupContext.placement.split('-')[0];

  return (
    <CssTransition
      className={`placement-${verticalPlacement}`}
      enterClassName="open"
      exitClassName="closed"
    >
      <Listbox {...other} ref={ref} />
    </CssTransition>
  );
});

AnimatedListbox.propTypes = {
  ownerState: PropTypes.object.isRequired,
};

const MenuItem = styled(BaseMenuItem)(
  ({ theme }) => `
  list-style: none;
  padding: 8px;
  border-radius: 8px;
  cursor: default;
  user-select: none;
  width: 300px;
  background-color: ${theme.palette.background.paper};
  color: ${theme.palette.text.primary};

  &:hover {
    background-color: ${theme.palette.action.hover};
  }

  &:last-of-type {
    border-bottom: none;
  }

  &.${menuItemClasses.focusVisible} {
    outline: 3px solid ${theme.palette.primary.main};
  }
  `,
);

const MenuButton = styled(BaseMenuButton, {
  shouldForwardProp: (prop) => prop !== 'allChecked',
})(
  ({ theme, allChecked }) => `
  font-family: 'IBM Plex Sans', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  line-height: 1.5;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 150ms ease;
  cursor: pointer;
  border: 1px solid ${theme.palette.divider};
  background-color: ${allChecked ? theme.palette.background.paper : theme.palette.error.main};
  color: ${theme.palette.text.primary};

  &:hover {
    background-color: ${allChecked ? theme.palette.action.hover : theme.palette.error.dark};
  }

  &:active {
    background-color: ${allChecked ? theme.palette.action.selected : theme.palette.error.dark};
  }

  &:focus-visible {
    outline: 3px solid ${theme.palette.primary.main};
  }
  `,
);
