from machine import UART, Pin
import time
import json


uart_rx = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=500)
LOG_FILE = "telemetry_log_base.jsonl"


def save_received_log(data_dict):
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
        received_text = raw_bytes.decode('utf-8').strip()
        
        if received_text:
            parsed_data = json.loads(received_text)
            print(f"[BASE] Dati validi ricevuti. Altitudine: {parsed_data} ")
            save_received_log(parsed_data)
            
    except ValueError:
        print(f"[BASE] Errore JSON (pacchetto corrotto o frammentato): {raw_bytes}")
      
    except Exception as e:
        print(f"[BASE] Errore imprevisto durante la decodifica: {e}")
     
     
     
def run_r():

    print("=== Avvio ricevitore LoRa in ascolto ===")
    
    while True:
      
        # Controlliamo se c'è qualcosa nel buffer
        if uart_rx.any():
            raw_data = uart_rx.readline()
            
            if raw_data:
                process_received_data(raw_data)
        
        # Pausa per non sovraccaricare la CPU
        time.sleep(0.1)
        
if __name__ == "__main__":
    run_r()
