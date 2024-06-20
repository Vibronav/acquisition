import { Container } from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';

const containerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  height: '100vh',
};


function LoadingBar() {
  return (
    <Container style={containerStyle}>
      <CircularProgress />
    </Container>
  );
}

export default LoadingBar;
