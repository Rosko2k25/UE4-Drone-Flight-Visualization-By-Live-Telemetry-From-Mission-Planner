#include "MAVLinkParser.h"

void UMAVLinkParser::ParseBytes(const TArray<uint8>& ByteArray)
{
    for (uint8 Byte : ByteArray)
    {
        if (mavlink_parse_char(MAVLINK_COMM_0, Byte, &Msg, &Status))
        {
            switch (Msg.msgid)
            {
            case MAVLINK_MSG_ID_HEARTBEAT:
            {
                mavlink_heartbeat_t heartbeat;
                mavlink_msg_heartbeat_decode(&Msg, &heartbeat);
                UE_LOG(LogTemp, Log, TEXT("HEARTBEAT received. Type: %d, Autopilot: %d"), heartbeat.type, heartbeat.autopilot);
                break;
            }

            case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
            {
                mavlink_global_position_int_t pos;
                mavlink_msg_global_position_int_decode(&Msg, &pos);
                float lat = pos.lat / 1E7f;
                float lon = pos.lon / 1E7f;
                float alt = pos.alt / 1000.0f;
                float vel = pos.vx / 100.0f;
                UE_LOG(LogTemp, Log, TEXT("Position: Lat %f, Lon %f, Alt %f, Vel %f"), lat, lon, alt, vel);
                break;
            }

            case MAVLINK_MSG_ID_ATTITUDE:
            {
                mavlink_attitude_t attitude;
                mavlink_msg_attitude_decode(&Msg, &attitude);
                UE_LOG(LogTemp, Log, TEXT("Attitude: Roll %f, Pitch %f, Yaw %f"),
                    FMath::RadiansToDegrees(attitude.roll),
                    FMath::RadiansToDegrees(attitude.pitch),
                    FMath::RadiansToDegrees(attitude.yaw));
                break;
            }

            // Add other MAVLink message handlers here as needed
            }
        }
    }
}