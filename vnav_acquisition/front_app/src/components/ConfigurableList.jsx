import React, { useState, useEffect } from 'react';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import {
    Checkbox,
    FormControl,
    IconButton,
    InputAdornment,
    InputLabel,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    OutlinedInput,
    Stack,
    Typography
} from '@mui/material';
import PropTypes from 'prop-types';

const ConfigurableList = ({
    title,
    addPrompt,
    defaultItems,
    addedItems,
    setAddedItems,
    checkedItems,
    setCheckedItems,
    height}) => {
    const [newItem, setNewItem] = useState('');

    const handleChooseItem = (value) => () => {
        const currentIndex = checkedItems.indexOf(value);
        const newCheckedItems = [...checkedItems];

        if (currentIndex === -1) {
            newCheckedItems.push(value);
        } else {
            newCheckedItems.splice(currentIndex, 1);
        }
        setCheckedItems(newCheckedItems);
    };

    const handleNewItemInput = (event) => {
        setNewItem(event.target.value);
    };

    const handleAddItem = () => {
        if (newItem && !addedItems.includes(newItem)) {
            setAddedItems(prevAddedItems => [...prevAddedItems, newItem]);
            setNewItem('');
        }
    };

    const handleDeleteItem = (item) => {
        setAddedItems(prevAddedItems => prevAddedItems.filter(i => i !== item));
        setCheckedItems(prevCheckedItems => prevCheckedItems.filter(i => i !== item));
    };

    return (
        <Stack sx={{ width: "100%", gap: 2 }}>
            <Typography variant="h6">{title}</Typography>
            <FormControl>
                <InputLabel>{addPrompt}</InputLabel>
                <OutlinedInput
                    endAdornment={
                        <InputAdornment position="end">
                            <IconButton
                                onClick={handleAddItem}
                                edge="end"
                                sx={{ '&:hover': { backgroundColor: '#f0f0f0' } }}>
                                <AddIcon sx={{ color: 'secondary.main' }} />
                            </IconButton>
                        </InputAdornment>
                    }
                    label={`${addPrompt}`}
                    value={newItem}
                    onChange={handleNewItemInput}
                />
            </FormControl>
            <List sx={{ width: '100%', maxHeight: { height }, overflow: 'auto', bgcolor: 'background.paper', borderRadius: 2 }}>
                {defaultItems.map((value) => {
                    const labelId = `checkbox-list-label-${value}`;
                    return (
                        <ListItem key={value} disablePadding>
                            <ListItemButton role={undefined} onClick={handleChooseItem(value)} dense>
                                <ListItemIcon>
                                    <Checkbox
                                        edge="start"
                                        checked={checkedItems.indexOf(value) !== -1}
                                        tabIndex={-1}
                                        disableRipple
                                        inputProps={{ 'aria-labelledby': labelId }}

                                    />
                                </ListItemIcon>
                                <ListItemText id={labelId} primary={value} />
                            </ListItemButton>
                        </ListItem>
                    );
                })}

                {addedItems.map((value) => {
                    const labelId = `checkbox-list-label-${value}`;
                    return (
                        <ListItem
                            key={value}
                            secondaryAction={
                                <IconButton
                                    edge="end"
                                    aria-label="delete"
                                    onClick={() => handleDeleteItem(value)}
                                    sx={{ '&:hover': { backgroundColor: '#f0f0f0' } }}>
                                    <DeleteOutlineIcon sx={{ color: 'secondary.main' }} />
                                </IconButton>
                            }
                            disablePadding
                        >
                            <ListItemButton role={undefined} onClick={handleChooseItem(value)} dense>
                                <ListItemIcon>
                                    <Checkbox
                                        edge="start"
                                        checked={checkedItems.indexOf(value) !== -1}
                                        tabIndex={-1}
                                        disableRipple
                                        inputProps={{ 'aria-labelledby': labelId }}

                                    />
                                </ListItemIcon>
                                <ListItemText id={labelId} primary={value} />
                            </ListItemButton>
                        </ListItem>
                    );
                })}
            </List>
        </Stack>
    );
};

ConfigurableList.propTypes = {
    title: PropTypes.string.isRequired,
    addPrompt: PropTypes.string.isRequired,
    defaultItems: PropTypes.array.isRequired,
    addedItems: PropTypes.array.isRequired,
    setAddedItems: PropTypes.func.isRequired,
    checkedItems: PropTypes.array.isRequired,
    setCheckedItems: PropTypes.func.isRequired,
    height: PropTypes.number

};

export default ConfigurableList;
