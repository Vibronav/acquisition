import { Stack } from '@mui/material';
import PropTypes from 'prop-types';
import React from 'react';
import { FormattedMessage } from 'react-intl';
import ConfigurableList from './ConfigurableList';

export default function ModifySpeeds({ config, setConfig }) {
    const [checkedSpeed, setCheckedSpeed] = React.useState(config.chosenSpeeds);
    const [addedSpeeds, setAddedSpeeds] = React.useState(config.newSpeeds);

    React.useEffect(() => {
        setCheckedSpeed(config.chosenSpeeds);
        setAddedSpeeds(config.newSpeeds);
    }, [config]);

    React.useEffect(() => {
        setConfig(prevConfig => ({
            ...prevConfig,
            chosenSpeeds: checkedSpeed,
            newSpeeds: addedSpeeds,
        }));
    }, [checkedSpeed, addedSpeeds, setConfig]);

    return (
        <Stack sx={{ width: "100%" }}>

            <ConfigurableList
                title={<FormattedMessage id="speed"></FormattedMessage>}
                addPrompt={<FormattedMessage id="addSpeed"></FormattedMessage>}
                defaultItems={config.defaultSpeeds}
                addedItems={addedSpeeds}
                setAddedItems={setAddedSpeeds}
                checkedItems={checkedSpeed}
                setCheckedItems={setCheckedSpeed}


            />
        </Stack>
    );
}

ModifySpeeds.propTypes = {
    config: PropTypes.object.isRequired,
    setConfig: PropTypes.func.isRequired,
};
