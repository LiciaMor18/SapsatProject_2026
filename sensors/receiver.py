from machine import UART, Pin
import time
import json

uart_rx = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), timeout=500)
LOG_FILE = "telemetry_log_base.jsonl"
  
def save_received_log(data_dict):
    """Salva i dati ricevuti in locale (append mode)."""
    try:
        # Aggiungiamo un timestamp di ricezione locale della base
        data_dict["rx_timestamp"] = time.ticks_ms()
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(data_dict) + "\n")
    except Exception as e:
        print(f"Errore salvataggio log base: {e}")
       
def process_received_data(raw_bytes):
    """Decodifica e processa i byte ricevuti."""
    try:
        # Decodifichiamo
        received_text = raw_bytes.decode('utf-8').strip()
        
        if received_text:
            parsed_data = json.loads(received_text)
            print(f"[BASE] Dati validi ricevuti: {parsed_data}")
            save_received_log(parsed_data)
            
    except ValueError:
        print(f"[BASE] Errore JSON (pacchetto corrotto o frammentato): {raw_bytes}")
    except Exception as e:
        print(f"[BASE] Errore imprevisto durante la decodifica: {e}")
       
def run_r():

    print("=== Avvio Ricevitore LoRa in ascolto ===")
    time.sleep(2)
    
    buffer = b""
    
    TIMEOUT_MS = 5000  # Tempo limite di silenzio (5000 ms = 5 secondi)
    last_rx_time = time.ticks_ms() # Registra l'ora in cui abbiamo iniziato
    is_connected = False # Partiamo dando per scontato di non essere connessi
    
    while True:
        
        # 1. CONTROLLO DISCONNESSIONE:
        # Se eravamo connessi, ma è passato troppo tempo dall'ultimo pacchetto...
        if is_connected and time.ticks_diff(time.ticks_ms(), last_rx_time) > TIMEOUT_MS:
            print("\n[ALLARME] Segnale dal SENDER perso! (Timeout superato)")
            is_connected = False # Segniamo che ci siamo disconnessi
            
            
        # 2. RICEZIONE DATI:
        # Controllo se c'è qualcosa in arrivo
        if uart_rx.any():
            # Leggiamo tutto 
            chunk = uart_rx.read()
            
            if chunk:
                # Abbiamo ricevuto qualcosa! 
                # Resettiamo il cronometro del watchdog
                last_rx_time = time.ticks_ms()
                
                # Se eravamo disconnessi, annunciamo il ritorno del segnale
                if not is_connected:
                    print("\n[BASE] Segnale dal SENDER attivo/ripristinato!")
                    is_connected = True
                
                # Aggiungiamo i nuovi pezzi al nostro buffer
                buffer += chunk
                
                if b'\n' in buffer:
                    # Dividiamo il buffer usando '\n' come separatore.
                    # Questo gestisce pacchetti attaccati
                    pacchetti = buffer.split(b'\n')
                    
                    # Tutti gli elementi tranne l'ultimo sono pacchetti completi
                    for pacchetto in pacchetti[:-1]:
                        if pacchetto: # Evitiamo di processare stringhe vuote
                            process_received_data(pacchetto)
                            
                    # L'ultimo frammento (che potrebbe essere incompleto) 
                    # diventa il nuovo buffer in attesa del resto dei dati
                    buffer = pacchetti[-1]
        
        time.sleep(0.05)
        
if __name__ == "__main__":
    run_r()
