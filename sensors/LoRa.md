# Wiring Documentation: LoRa E220-900T22D to Raspberry Pi

This document describes the hardware connection between the two **Ebyte E220-900T22D** LoRa modules and the **Raspberry Pi** 
to transmit messages between the sky and the ground station.

## Sender & Receiver hardware connections

The following table shows the pin-to-pin mapping between the LoRa modules and the Raspberry Pi GPIO header.
They are the same for sender and receiver

| LoRa Module Pin | Raspberry Pi Pico Pin | Pico Function | Description |
| :--- | :--- | :--- | :--- |
| **VCC** | **VBUS** (Pin 40) | 5V Power | Powered directly from USB 5V |
| **GND** | **GND** | Ground | Common ground |
| **RXD** | **GP0** (Pin 1) | UART0 TX | LoRa RX connected to Pico TX |
| **TXD** | **GP1** (Pin 2) | UART0 RX | LoRa TX connected to Pico RX |
| **M0** | **GND** | Ground | Hardwired to GND (Normal Mode) |
| **M1** | **GND** | Ground | Hardwired to GND (Normal Mode) |
| **AUX** | *Not Connected* | - | Status indicator ignored in this setup |

> [!CAUTION]
> Do not use 3V power it won't turn on the connection because this module need 5V power.

---

## Setup Notes

* **Operating Mode**: because both `M0` and `M1` are connected directly to GND, the module is locked in **Normal Mode** (Mode 0).
  It will act as a transparent serial bridge. You cannot enter Sleep or Configuration mode via software with this wiring.
  
* **Serial Communication**: ensure the pico code initializes `UART0` using `GP0` as TX and `GP1` as RX at a default baud rate of 9600 bps. (code)
  
* **Hardware Status (AUX)**: the `AUX` pin is intentionally disconnected. The code implements check on the buffer to prevent 
