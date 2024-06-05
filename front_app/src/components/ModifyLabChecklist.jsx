import React from 'react';
import { Stack } from '@mui/material';
import PropTypes from 'prop-types';
import ConfigurableList from './ConfigurableList';

export default function ModifyLabChecklist({ config, setConfig }) {
    const [checkedItems, setCheckedItems] = React.useState(config.chosen_lab_checks);
    const [addedItems, setAddedItems] = React.useState(config.new_lab_checks);


    React.useEffect(() => {
        setCheckedItems(config.chosen_lab_checks);
    }, [config]);

    React.useEffect(() => {
        setConfig(prevConfig => ({
            ...prevConfig,
            chosen_lab_checks: checkedItems,
            new_lab_checks: addedItems,

        }));
    }, [checkedItems, addedItems, setConfig]);

    return (
        <Stack sx={{ width: "100%" }}>
            <ConfigurableList
                title="Before Measurement"
                addPrompt="Add task"
                defaultItems={config.lab_checks}
                addedItems={addedItems}
                setAddedItems={setAddedItems}
                checkedItems={checkedItems}
                setCheckedItems={setCheckedItems}
                height={250}

            />
        </Stack>
    );
}

ModifyLabChecklist.propTypes = {
    config: PropTypes.object.isRequired,
    setConfig: PropTypes.func.isRequired,
};