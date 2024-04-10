import { createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    background: {
      default: '#121212', // Use consistent dark background
      paper: '#1a1a1a', // Slightly lighter paper for contrast
    },
    primary: {
      main: '#3f51b5', // Maintain primary color
    },
    secondary: {
      main: '#f57c00', // Maintain secondary color
    },
    text: {
      primary: '#cccccc', // Use lighter text on dark background
      secondary: '#b0b0b0', // Slightly darker secondary text
    },
  },
  typography: {
    fontFamily: [
      '"Roboto"',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiAppBar: {
      defaultProps: {
        color: 'primary',
        elevation: 0, // Remove elevation for a seamless look
      },
    },
    MuiButton: {
      defaultProps: {
        variant: 'contained',
        color: 'primary',
      },
      styleOverrides: {
        contained: {
          backgroundColor: '#3f51b5',
          '&:hover': {
            backgroundColor: '#303fbc',
          },
        },
        text: {
          color: '#e0e0e0', // Ensure text contrast on dark buttons
          '&:hover': {
            // Consider a subtle text color hover effect
          },
        },
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 0, // Remove elevation for a flatter look
      },
      styleOverrides: {
        root: {
          // Consider subtle box-shadow for depth on hover
        },
      },
    },
    MuiInput: {
      styleOverrides: {
        underline: {
          '&:before': {
            borderBottom: '1px solid #e0e0e0',
          },
          '&:hover:not(.Mui-focused):not(.Mui-disabled)&:before': {
            borderBottom: '2px solid #f57c00',
          },
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#e0e0e0',
        },
      },
    },
  },
});

export default darkTheme;
