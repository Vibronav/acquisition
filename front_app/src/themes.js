import { createTheme } from '@mui/material/styles';

export const darkTheme = createTheme({
    palette: {
        type: 'dark',
        background: {
            default: "#404045",
            paper: "#424242"
        },
        primary: {
            main: '#568166',
            contrastText: "#fff"
        },
        secondary: {
            main: '#fb8c00',
            contrastText: "rgba(0, 0, 0, 0.87)"
        },
        text: {
            primary: '#fff',
            secondary: "rgba(255, 255, 255, 0.7)",
            disabled: "rgba(255, 255, 255, 0.5)",
            hint: "rgba(255, 255, 255, 0.5)"
        },
        divider: "rgba(255, 255, 255, 0.12)",
    },




});

export const lightTheme = createTheme({
    palette: {
        type: 'light',
        primary: {
            main: '#568166',
        },
        secondary: {
            main: '#fb8c00',
        },
    },
});

export const selectStyles = {
    '.MuiOutlinedInput-notchedOutline': {
        borderColor: '#181c18',

    },
    size: "small"
    
    


}

export const stackStyles = {
    width: "100%",
    gap: 1
}


export const formControlStyles = {

    width: "100%",
    size: "small"

}