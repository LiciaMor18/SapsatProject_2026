# Rui Santos & Sara Santos - Random Nerd Tutorials
# Modificato per creare un file CSV
from machine import SPI, Pin
import sdcard, os

# Costanti
SPI_BUS = 0
SCK_PIN = 2
MOSI_PIN = 3
MISO_PIN = 4
CS_PIN = 5
SD_MOUNT_PATH = '/sd'

try:
    # Inizializzazione comunicazione SPI
    spi = SPI(SPI_BUS, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
    cs = Pin(CS_PIN)
    sd = sdcard.SDCard(spi, cs)
    
    # Montaggio della MicroSD
    os.mount(sd, SD_MOUNT_PATH)
    print("Scheda SD montata correttamente.")

    # --- NUOVA PARTE: CREAZIONE FILE CSV ---
    # Definiamo il percorso completo del file
    file_path = SD_MOUNT_PATH + '/text.csv'
    
    print("Creazione del file text.csv...")
    # 'w' sta per "write" (scrittura). Se il file esiste, verrà sovrascritto.
    with open(file_path, 'w') as f:
        # Intestazione del CSV
        f.write("Data,Ora,Temperatura\n")
        # Una riga di esempio
        f.write("2023-10-27,10:30,22.5\n")
        f.write("2023-10-27,11:30,23.1\n")
    
    print("File creato con successo!")
    # ---------------------------------------

    # Elenca i file sulla MicroSD per confermare la creazione
    print("File presenti sulla SD:", os.listdir(SD_MOUNT_PATH))

except Exception as e:
    print('Si è verificato un errore:', e)