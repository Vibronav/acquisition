import PropTypes from 'prop-types';
import { Box, Typography } from '@mui/material'

Error.propTypes = {
  msg: PropTypes.string.isRequired
}

function Error({msg}) {
  return (
    <Box sx={{backgroundColor: "white", width: "50%", color: 'black', border: '1px solid black', borderRadius: "10px", 
    p: 10, alignItems: "center"}}>
        <Typography variant='h6' fontWeight='bold'>
            500 Internal Server Error
        </Typography>
        <Typography> 
            There was a problem while trying to get {msg}
        </Typography>
    </Box>
  )
}

export default Error
