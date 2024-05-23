# Refactoring TODOs

## Karolina:
- [ ] *Protocol Checklist : Ensure a checklist is in place before measurements, which resets when changing materials. -> ustawienie kamery, I in. (Ask Hamza) - > w formie pop up’a/ bardziej warningu  po zmianie materiału
- [x] *Parameter Adjustment via Interface: Allow users to modify parameters directly through the interface instead of relying solely on JSON files. We also should able to select users. Powinien by json z domyślnymi użytkownikami ale w sesji powinna być możliwość dodania nowych użytkowników bez nadpisywania domyślnej listy.
- [ ] Finetuning Configuration Change: speeds -> change to „właściwości” (walidacja materiały prędkości -> przynajmniej jeden materiał, username -> musi być nazwoplikowy)
- [ ] Measurement Counting: Enable the system to count measurements for each user, material, and their combinations, providing statistics such as "Hamza: Breast = 30," for example.
- [x] Ask Hamza???  Recording Confirmation: The app must prevent new recordings until successfully saving previous files.
- [x] Kontakt ze studentem który robi sterowanie robotem. Maksym Bodnar
- [x] Ensure no _ in username (JS)
- [x] Second Camera Integration: Utilize a secondary camera for top-down recording to provide additional perspectives during measurements.

## Adam:
- [x] Do sprawdzenia instalacja node.js -> wszystko powinno być instalowane przez pip jako pakiet / GitHub pages / serwer agh / docker
- [ ] Recording to mp4 (JS or Python)

## Unassigned:
- [x] Refactoring (JS)
- [ ] Dodanie możliwości resetu (bezpiecznego)
- [ ] Keyboard Shortcuts: Implement keyboard shortcuts for commonly used functions like start, stop, etc., to enhance user convenience and efficiency.
- [ ] Display of recorded wave (matplotlib@Python + JS)
- [ ] Voice commands (JS: Web Speech API)
- [ ] Automatic Video Saving-Deleting: Videos should automatically save upon pressing the stop button, like audio files. Additionally, include options to delete the last recorded audio and video files separately or simultaneously.