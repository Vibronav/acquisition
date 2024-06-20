import { Stack } from '@mui/material';
import PropTypes from 'prop-types';
import React from 'react';
import { FormattedMessage } from 'react-intl';
import ConfigurableList from './ConfigurableList';

export default function ModifyMaterials({ config, setConfig }) {
  const [checkedMaterial, setCheckedMaterial] = React.useState(config.chosenMaterials);
  const [addedMaterials, setAddedMaterials] = React.useState(config.newMaterials);

  React.useEffect(() => {
    setCheckedMaterial(config.chosenMaterials);
    setAddedMaterials(config.newMaterials);
  }, [config]);

  React.useEffect(() => {
    setConfig(prevConfig => ({
      ...prevConfig,
      chosenMaterials: checkedMaterial,
      newMaterials: addedMaterials,
    }));
  }, [checkedMaterial, addedMaterials, setConfig]);

  return (
    <Stack sx={{ width: "100%" }}>
      <ConfigurableList
        title={<FormattedMessage id="material"></FormattedMessage>}
        addPrompt={<FormattedMessage id="addMaterial"></FormattedMessage>}
        defaultItems={config.defaultMaterials}
        addedItems={addedMaterials}
        setAddedItems={setAddedMaterials}
        checkedItems={checkedMaterial}
        setCheckedItems={setCheckedMaterial}
        height={430}
      />
    </Stack>

  );
}

ModifyMaterials.propTypes = {
  config: PropTypes.object.isRequired,
  setConfig: PropTypes.func.isRequired,
};
