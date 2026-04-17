from machine import UART, Pin
import time
import json

uart_tx = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), timeout=500)
LOG_FILE = "telemetry_log_sender.jsonl"

def read_sensors(alt, temp, batt, rate, ang, acc, mag):
    """
    Riceve i dati in input dai sensori e restituisce il dizionario formattato.
    """
    return {
        "alt": alt,
        "temp": temp,
        "batt": batt,
        "rate": rate,
        "ang": ang,
        "acc": acc,
        "mag": mag
    }

def save_local_log(telemetry):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(telemetry) + "\n")
          
    except Exception as e:
        print(f"Errore salvataggio log: {e}")

def run_s():
  
    print("=== Avvio test Telemetria LoRa per invio ===")
        
    while True:
        
        # Valori di PROVA
        current_alt = 1042.5
        current_temp = 18.5
        current_batt = 3.74
        current_rate = 12.3
        current_ang = [0.05, -0.1, 0]
        current_acc = [0.0, 0.0, 9.81]
        current_mag = [25, -12, 45]
      
        telemetry_data = read_sensors(
            current_alt, current_temp, current_batt, current_rate, 
            current_ang, current_acc, current_mag
        )
        
        payload = json.dumps(telemetry_data) + "\n"
        
        print("\n[SONDA] Inviando dati...")
        
        # Trasmissione
        start_time = time.ticks_ms()
        uart_tx.write(payload.encode('utf-8'))
        end_time = time.ticks_ms()
        
        send_duration_ms = time.ticks_diff(end_time, start_time)
        print(f"[SONDA] Dati inviati. Tempo di esecuzione UART: {send_duration_ms} ms")
        
        telemetry_data["sys_send_time_ms"] = send_duration_ms
        telemetry_data["timestamp"] = time.ticks_ms()
        
        save_local_log(telemetry_data)
        
        time.sleep(1)
    
    
if __name__ == "__main__":
    run_s()
