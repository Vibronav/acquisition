import * as React from 'react';
import { ClickAwayListener } from '@mui/base/ClickAwayListener';
import { Typography, Button, Box } from '@mui/material';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

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
                    Keyboard Shortcuts

                </Button>
                {open ? (
                    <Box sx={{position: 'absolute', backgroundColor: 'primary.main', padding: 3, borderRadius: 2, width: 'max-content'}}>
                        <Typography >
                            <b>Ctrl + Shift + R</b>: Start / Stop Recording
                        </Typography>
                        <Typography >
                        <b>Ctrl + Shift + D</b>: Delete Last Recording
                        </Typography>
                    </Box>
                ) : null}
            </Box>
        </ClickAwayListener>
    );
}

