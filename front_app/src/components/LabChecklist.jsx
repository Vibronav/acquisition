import { ClickAwayListener } from '@mui/base/ClickAwayListener';
import CheckIcon from '@mui/icons-material/Check';
import ErrorIcon from '@mui/icons-material/Error';
import { Button, Checkbox, List, ListItem, ListItemButton, ListItemText } from '@mui/material';
import Box from '@mui/material/Box';
import PropTypes from 'prop-types';
import * as React from 'react';
import { FormattedMessage } from 'react-intl';

export default function LabChecklist({ config }) {
    const [open, setOpen] = React.useState(false);
    const [tasks, setTasks] = React.useState(config.chosen_lab_checks);

    const handleClick = () => {
        setOpen((prev) => !prev);
    };

    const handleClickAway = () => {
        setOpen(false);
    };

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

    // Define styles conditionally based on allChecked
    const buttonStyles = {
        backgroundColor: !allChecked &&  'error.main',
        '&:hover': {
            backgroundColor: !allChecked && 'error.main',
        },
        '&:active': {
            backgroundColor: !allChecked && 'error.main',
        },
    };

    return (
        <ClickAwayListener onClickAway={handleClickAway}>
            <Box sx={{ position: 'relative' }}>
                <Button
                    variant="contained"
                    onClick={handleClick}
                    sx={buttonStyles}
                >
                    {<FormattedMessage id="beforeMessurmentsChecklist"></FormattedMessage>}
                    {allChecked ? <CheckIcon /> : <ErrorIcon />}
                </Button>
                {open ? (
                    <List sx={{ width: '100%', maxHeight: 300, overflow: 'auto', bgcolor: 'background.paper', borderRadius: '0% 0% 2% 2%' }}>
                        {tasks.map((task) => (
                            <ListItem key={task} disablePadding>
                                <ListItemButton onClick={createHandleCheckboxChange(task)} dense>
                                    <Checkbox
                                        checked={!!checkedItems[task]}
                                        onChange={createHandleCheckboxChange(task)}
                                    />
                                    {task}
                                    <ListItemText />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                ) : null}
            </Box>
        </ClickAwayListener>
    );
}

LabChecklist.propTypes = {
    config: PropTypes.shape({
        chosen_lab_checks: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
};