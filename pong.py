import asyncio
import pygame
from bleak import BleakScanner, BleakClient
import time

# BLE device and characteristic UUIDs
device_name = "Nano RP2040"
characteristic_uuid = "87654321-4321-4321-4321-abc987654321"

# Initialize Pygame
pygame.init()

# Screen settings
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
size = (800, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pong with BLE Control")

# Paddle and ball settings
rect_x = 400
rect_y = 580
rect_change_x = 0
ball_x, ball_y = 50, 50
ball_change_x, ball_change_y = 5, 5
score = 0

# Flag to check if game should start
gy_value = 0  # Placeholder for gyroscope Y-axis data

# Draw the paddle
def draw_paddle(screen, x, y):
    x = max(0, min(x, size[0] - 100))  # Constrain paddle to screen width
    pygame.draw.rect(screen, RED, [x, y, 100, 20])

async def find_device_address():
    """Scans for nearby BLE devices and returns the address of the device with the specified name."""
    while True:
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        for device in devices:
            if device.name == device_name:
                print(f"Found device: {device.name} with address {device.address}")
                return device.address
        time.sleep(2)
    return None

# Game loop function
async def game_loop():
    global rect_x, rect_change_x, ball_x, ball_y, ball_change_x, ball_change_y, score, gy_value

    # Connect to BLE device
    device_address = await find_device_address()
    if device_address is None:
        print("Unable to find the device. Exiting...")
        return

    async with BleakClient(device_address) as client:
        if client.is_connected:
            print("Connected to device")

            clock = pygame.time.Clock()
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True

                # Read gyroscope data from BLE device
                try:
                    data = await client.read_gatt_char(characteristic_uuid)
                    delta_y = int.from_bytes(data, byteorder='little', signed=True)
                    gy_value += delta_y
                    if gy_value > 60:
                        gy_value = 60
                    elif gy_value < -60:
                        gy_value = -60
                    print("Received gy:", delta_y, " gy_val:", gy_value)

                except Exception as e:
                    print("Error reading characteristic:", e)
                    done = True
                    break

                # Update paddle position based on gyroscope data
                rect_x += gy_value // 10  # Scale gyroscope value to control paddle
                rect_x = max(0, min(rect_x, size[0] - 100))  # Constrain paddle to screen width

                # Update ball position
                ball_x += ball_change_x
                ball_y += ball_change_y

                # Ball collision logic
                if ball_x < 0 or ball_x > size[0] - 15:
                    ball_change_x *= -1
                if ball_y < 0 or (rect_x < ball_x < rect_x + 100 and ball_y >= rect_y - 15):
                    ball_change_y *= -1
                    if ball_y >= rect_y - 15:
                        score += 1
                if ball_y > size[1]:
                    ball_change_y *= -1
                    score = 0  # Reset score if ball hits the bottom

                # Draw everything
                screen.fill(BLACK)
                pygame.draw.rect(screen, WHITE, [ball_x, ball_y, 15, 15])
                draw_paddle(screen, rect_x, rect_y)

                # Display score
                font = pygame.font.SysFont('Calibri', 15, False, False)
                score_text = font.render("Score = " + str(score), True, WHITE)
                screen.blit(score_text, [600, 100])

                pygame.display.flip()
                clock.tick(60)

    pygame.quit()

# Start the program
asyncio.run(game_loop())
