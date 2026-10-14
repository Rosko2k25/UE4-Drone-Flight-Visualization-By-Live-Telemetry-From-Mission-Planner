import asyncio
from mavsdk import System
import socket
import struct

UNREAL_HOST = '127.0.0.1'
UNREAL_PORT = 5005

# Queue to hold latest telemetry for sending
telemetry_queue = asyncio.Queue()

async def send_to_unreal(conn):
    while True:
        lat, lon, alt, speed, roll, pitch, yaw = await telemetry_queue.get()
        data = struct.pack('fffffff', lat, lon, alt, speed, roll, pitch, yaw)
        try:
            conn.sendall(data)
        except Exception as e:
            print(f"[ERROR] Failed to send data to Unreal: {e}")
            break
        await asyncio.sleep(0.1)

async def collect_telemetry(drone):
    async for position in drone.telemetry.position():
        latest_position = position
        break

    async for velocity in drone.telemetry.velocity_ned():
        latest_velocity = velocity
        break

    async for attitude in drone.telemetry.attitude_euler():
        latest_attitude = attitude
        break

    print("Telemetry streams confirmed, starting loop...")

    # Start streaming telemetry
    async for position in drone.telemetry.position():
        velocity = await drone.telemetry.velocity_ned().__anext__()
        attitude = await drone.telemetry.attitude_euler().__anext__()

        lat = position.latitude_deg
        lon = position.longitude_deg
        alt = position.absolute_altitude_m

        vx = velocity.north_m_s
        vy = velocity.east_m_s
        vz = velocity.down_m_s
        speed = (vx**2 + vy**2 + vz**2)**0.5

        roll = attitude.roll_deg
        pitch = attitude.pitch_deg
        yaw = attitude.yaw_deg

        print(f"Send: lat={lat:.6f}, lon={lon:.6f}, alt={alt:.2f}, spd={speed:.2f}, rpy={roll:.1f}/{pitch:.1f}/{yaw:.1f}")
        await telemetry_queue.put((lat, lon, alt, speed, roll, pitch, yaw))

        await asyncio.sleep(0.05)

async def main():
    print(f"Listening for Unreal on {UNREAL_HOST}:{UNREAL_PORT}...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UNREAL_HOST, UNREAL_PORT))
    server_socket.listen(1)

    conn, addr = server_socket.accept()
    print(f"Unreal connected from {addr}")

    drone = System(mavsdk_server_address='localhost', port=50051)
    await drone.connect(system_address="udp://:14560")

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    await asyncio.gather(
        collect_telemetry(drone),
        send_to_unreal(conn)
    )

if __name__ == "__main__":
    asyncio.run(main())