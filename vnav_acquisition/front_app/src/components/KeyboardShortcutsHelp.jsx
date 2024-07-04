import { ClickAwayListener } from '@mui/base/ClickAwayListener';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import { Box, Button, Typography } from '@mui/material';
import * as React from 'react';
import { FormattedMessage } from 'react-intl';

export default function KeyboardShortcutsHelp() {
    const [open, setOpen] = React.useState(false);

    const handleClick = () => {
        setOpen((prev) => !prev);
    };

    const handleClickAway = () => {
        setOpen(false);
    };


    return (
        <ClickAwayListener onClickAway={handleClickAway}>
            <Box sx={{ position: 'relative', marginRight: 10 }}>
                <Button
                    onClick={handleClick}
                    sx={{color: 'primary.contrastText'}}
            
                >
                    <QuestionMarkIcon></QuestionMarkIcon>
                    {<FormattedMessage id="keyboardShortcuts"></FormattedMessage>}

                </Button>
                {open ? (
                    <Box sx={{position: 'absolute', backgroundColor: 'primary.main', padding: 3, borderRadius: 2, width: 'max-content'}}>
                        <Typography >
                            <b>Ctrl + Shift + R</b>: {<FormattedMessage id="keyboardShortcutsStart"></FormattedMessage>}
                        </Typography>
                        <Typography >
                        <b>Ctrl + Shift + D</b>: {<FormattedMessage id="keyboardShortcutsDelete"></FormattedMessage>}
                        </Typography>
                    </Box>
                ) : null}
            </Box>
        </ClickAwayListener>
    );
}

