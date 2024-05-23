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
import { darkTheme } from '../themes'; // Assuming you are importing the darkTheme correctly

export default function LabChecklist() {
  const [checkedItems, setCheckedItems] = React.useState({
    profile: false,
    languageSettings: false,
    logOut: false,
  });

  const createHandleCheckboxChange = (item) => {
    return (event) => {
      setCheckedItems((prevState) => ({
        ...prevState,
        [item]: event.target.checked,
      }));
    };
  };

  const allChecked = Object.values(checkedItems).every(Boolean);

  return (
    <Container sx={{ width: '100%', justifyContent: 'right', display: 'flex' }}>
      <Dropdown>
        <MenuButton sx={{ width: '30%' }} allChecked={allChecked}>
          Before Measurement Checklist
        </MenuButton>
        <Menu slots={{ listbox: AnimatedListbox }}>
          <MenuItem onClick={createHandleCheckboxChange('profile')}>
            <Checkbox checked={checkedItems.profile} onChange={createHandleCheckboxChange('profile')} />
            Quiet room/greyuce external noises
          </MenuItem>
          <MenuItem onClick={createHandleCheckboxChange('languageSettings')}>
            <Checkbox checked={checkedItems.languageSettings} onChange={createHandleCheckboxChange('languageSettings')} />
            Set background white screen
          </MenuItem>
          <MenuItem onClick={createHandleCheckboxChange('logOut')}>
            <Checkbox checked={checkedItems.logOut} onChange={createHandleCheckboxChange('logOut')} />
            Set camera angle
          </MenuItem>
        </Menu>
      </Dropdown>
    </Container>
  );
}

const grey = '#111';

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
